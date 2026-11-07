import re
from decimal import ROUND_HALF_UP, Decimal, DecimalException

from contract import Classification, CompanyScreen, CovenantStatus, Reason

from .checks import result
from .fixtures import COMPANIES, SCALES, find

MAX_DECIMAL_CHARACTERS = 64
MAX_ABSOLUTE_THRESHOLD = Decimal("1e18")
MIN_DECIMAL_EXPONENT = -18
MAX_DECIMAL_EXPONENT = 18
DECIMAL_PATTERN = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")


def bounded_nonnegative_decimal(text):
    if not 1 <= len(text) <= MAX_DECIMAL_CHARACTERS or DECIMAL_PATTERN.fullmatch(text) is None:
        return None
    try:
        number = Decimal(text)
        if not number.is_finite():
            return None
        exponent = number.as_tuple().exponent
        if exponent < MIN_DECIMAL_EXPONENT or exponent > MAX_DECIMAL_EXPONENT:
            return None
        if number < 0 or number > MAX_ABSOLUTE_THRESHOLD:
            return None
    except DecimalException:
        return None
    return number


def value(row):
    return Decimal(row["value"]) * Decimal(SCALES[row["unit_scale"]])


def sources(rows):
    return [row["source_id"] for row in rows if row is not None]


def display(ratio):
    return format(ratio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")


def company_screen(company, year, maximum, minimum):
    debt, ebitda = find(company, year, "Debt"), find(company, year, "EBITDA")
    ebit, interest = find(company, year, "EBIT"), find(company, year, "Interest expense")
    reasons = []
    if debt is None:
        leverage_status, leverage_ratio = CovenantStatus.UNEVALUABLE, ""
        reasons.append(Reason.MISSING_DEBT)
    elif ebitda is None:
        leverage_status, leverage_ratio = CovenantStatus.UNEVALUABLE, ""
        reasons.append(Reason.MISSING_EBITDA)
    elif value(ebitda) <= 0:
        leverage_status, leverage_ratio = CovenantStatus.UNEVALUABLE, ""
        reasons.append(Reason.NONPOSITIVE_EBITDA)
    else:
        raw = value(debt) / value(ebitda)
        leverage_status = CovenantStatus.PASS if raw <= maximum else CovenantStatus.FAIL
        leverage_ratio = display(raw)
        if leverage_status == CovenantStatus.FAIL:
            reasons.append(Reason.LEVERAGE_EXCEEDS_MAXIMUM)
    if ebit is None:
        coverage_status, coverage_ratio = CovenantStatus.UNEVALUABLE, ""
        reasons.append(Reason.MISSING_EBIT)
    elif interest is None:
        coverage_status, coverage_ratio = CovenantStatus.UNEVALUABLE, ""
        reasons.append(Reason.MISSING_INTEREST_EXPENSE)
    elif value(interest) <= 0:
        coverage_status, coverage_ratio = CovenantStatus.UNEVALUABLE, ""
        reasons.append(Reason.NONPOSITIVE_INTEREST_EXPENSE)
    else:
        raw = value(ebit) / value(interest)
        coverage_status = CovenantStatus.PASS if raw >= minimum else CovenantStatus.FAIL
        coverage_ratio = display(raw)
        if coverage_status == CovenantStatus.FAIL:
            reasons.append(Reason.COVERAGE_BELOW_MINIMUM)
    statuses = (leverage_status, coverage_status)
    classification = (
        Classification.FAIL
        if CovenantStatus.FAIL in statuses
        else Classification.INSUFFICIENT_DATA
        if CovenantStatus.UNEVALUABLE in statuses
        else Classification.PASS
    )
    return CompanyScreen(
        company,
        classification,
        leverage_status,
        leverage_ratio,
        sources([debt, ebitda]),
        coverage_status,
        coverage_ratio,
        sources([ebit, interest]),
        reasons,
    )


def expected(arguments):
    if (
        arguments.fiscal_year != "FY2024"
        or not arguments.companies
        or len(arguments.companies) != len(set(arguments.companies))
        or any(company not in COMPANIES for company in arguments.companies)
    ):
        return None
    maximum = bounded_nonnegative_decimal(arguments.maximum_leverage)
    minimum = bounded_nonnegative_decimal(arguments.minimum_interest_coverage)
    if maximum is None or minimum is None:
        return None
    screens = [company_screen(company, arguments.fiscal_year, maximum, minimum) for company in arguments.companies]
    classes = [screen.classification for screen in screens]
    overall = (
        Classification.FAIL
        if Classification.FAIL in classes
        else Classification.INSUFFICIENT_DATA
        if Classification.INSUFFICIENT_DATA in classes
        else Classification.PASS
    )
    return overall, screens


def verify_task(arguments, output, reference, workspace):
    wanted = expected(arguments)
    if wanted is None:
        return result(
            False,
            "companies must be nonempty, unique, and known; thresholds must be finite nonnegative ASCII decimals "
            "of at most 64 characters, decimal exponent from -18 through 18, and value at most 1e18",
        )
    if output is None:
        return result(False, "missing task submission")
    valid = (output.overall, output.companies) == wanted
    return result(
        valid,
        "covenant screen is correct"
        if valid
        else "coverage, ratios, sources, reasons, classifications, or overall result is incorrect",
    )

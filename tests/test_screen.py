import pytest
from slimconfig import build_output

import verifier
from contract import (
    Classification,
    CompanyScreen,
    CovenantStatus,
    ListCovenantFactsInput,
    ReadCovenantFactInput,
    Reason,
    ScreenCovenantsInput,
    ScreenCovenantsOutput,
)
from plugin import list_covenant_facts, read_covenant_fact


def company(name, classification, lev_status, lev_ratio, lev_sources, cov_status, cov_ratio, cov_sources, reasons=()):
    return CompanyScreen(
        name, classification, lev_status, lev_ratio, lev_sources, cov_status, cov_ratio, cov_sources, list(reasons)
    )


def args(names, maximum="2", minimum="5"):
    return ScreenCovenantsInput(names, "FY2024", maximum, minimum)


def check(given, output):
    return verifier.verify_task("screen-covenants", given, output, None, ".")


def test_equality_boundaries_pass():
    row = company(
        "Equality Holdings",
        Classification.PASS,
        CovenantStatus.PASS,
        "2.00",
        ["EH-DEBT", "EH-EBITDA"],
        CovenantStatus.PASS,
        "5.00",
        ["EH-EBIT", "EH-INT"],
    )
    assert check(args(["Equality Holdings"]), ScreenCovenantsOutput(Classification.PASS, [row]))["valid"] is True


def test_exact_comparison_before_display_rounding():
    high = company(
        "High Leverage Co",
        Classification.FAIL,
        CovenantStatus.FAIL,
        "2.00",
        ["HL-DEBT", "HL-EBITDA"],
        CovenantStatus.PASS,
        "6.00",
        ["HL-EBIT", "HL-INT"],
        [Reason.LEVERAGE_EXCEEDS_MAXIMUM],
    )
    low = company(
        "Low Coverage Co",
        Classification.FAIL,
        CovenantStatus.PASS,
        "1.00",
        ["LC-DEBT", "LC-EBITDA"],
        CovenantStatus.FAIL,
        "5.00",
        ["LC-EBIT", "LC-INT"],
        [Reason.COVERAGE_BELOW_MINIMUM],
    )
    under = company(
        "Just Under Co",
        Classification.PASS,
        CovenantStatus.PASS,
        "2.00",
        ["JU-DEBT", "JU-EBITDA"],
        CovenantStatus.PASS,
        "5.00",
        ["JU-EBIT", "JU-INT"],
    )
    assert (
        check(
            args(["High Leverage Co", "Low Coverage Co", "Just Under Co"]),
            ScreenCovenantsOutput(Classification.FAIL, [high, low, under]),
        )["valid"]
        is True
    )


def test_missing_and_nonpositive_denominators():
    missing = company(
        "Missing Metrics Co",
        Classification.INSUFFICIENT_DATA,
        CovenantStatus.PASS,
        "2.00",
        ["MM-DEBT", "MM-EBITDA"],
        CovenantStatus.UNEVALUABLE,
        "",
        ["MM-EBIT"],
        [Reason.MISSING_INTEREST_EXPENSE],
    )
    nonpositive = company(
        "Nonpositive Co",
        Classification.INSUFFICIENT_DATA,
        CovenantStatus.UNEVALUABLE,
        "",
        ["NP-DEBT", "NP-EBITDA"],
        CovenantStatus.UNEVALUABLE,
        "",
        ["NP-EBIT", "NP-INT"],
        [Reason.NONPOSITIVE_EBITDA, Reason.NONPOSITIVE_INTEREST_EXPENSE],
    )
    assert (
        check(
            args(["Missing Metrics Co", "Nonpositive Co"]),
            ScreenCovenantsOutput(Classification.INSUFFICIENT_DATA, [missing, nonpositive]),
        )["valid"]
        is True
    )


def test_known_failure_overrides_another_missing_ratio():
    row = company(
        "Known Fail Missing Co",
        Classification.FAIL,
        CovenantStatus.FAIL,
        "3.00",
        ["KF-DEBT", "KF-EBITDA"],
        CovenantStatus.UNEVALUABLE,
        "",
        ["KF-EBIT"],
        [Reason.LEVERAGE_EXCEEDS_MAXIMUM, Reason.MISSING_INTEREST_EXPENSE],
    )
    assert check(args(["Known Fail Missing Co"]), ScreenCovenantsOutput(Classification.FAIL, [row]))["valid"] is True


def test_wrong_coverage_duplicate_company_and_missing_submission_rejected():
    wrong = company(
        "Equality Holdings",
        Classification.PASS,
        CovenantStatus.PASS,
        "2.00",
        ["HL-DEBT", "EH-EBITDA"],
        CovenantStatus.PASS,
        "5.00",
        ["EH-EBIT", "EH-INT"],
    )
    assert check(args(["Equality Holdings"]), ScreenCovenantsOutput(Classification.PASS, [wrong]))["valid"] is False
    assert (
        check(args(["Equality Holdings", "Equality Holdings"]), ScreenCovenantsOutput(Classification.PASS, []))["valid"]
        is False
    )
    assert check(args(["Equality Holdings"]), None)["valid"] is False


def test_malformed_threshold_year_and_output_rejected():
    assert (
        check(args(["Equality Holdings"], maximum="bad"), ScreenCovenantsOutput(Classification.PASS, []))["valid"]
        is False
    )
    invalid_year = ScreenCovenantsInput(["Equality Holdings"], "FY2023", "2", "5")
    assert check(invalid_year, ScreenCovenantsOutput(Classification.PASS, []))["valid"] is False
    with pytest.raises(ValueError, match="missing field"):
        build_output({"overall": "pass"}, ScreenCovenantsOutput)
    with pytest.raises(ValueError, match="not a valid Classification"):
        build_output({"overall": "maybe", "companies": []}, ScreenCovenantsOutput)


def test_tools_fixtures_and_determinism():
    given = ListCovenantFactsInput("Equality Holdings")
    listed = list_covenant_facts(given)
    assert len(listed.facts) == 4 and verifier.verify_output("list_covenant_facts", given, listed, ".")["valid"] is True
    read_given = ReadCovenantFactInput("HL-DEBT")
    read = read_covenant_fact(read_given)
    assert (
        "200010 USD thousand" in read.excerpt
        and verifier.verify_output("read_covenant_fact", read_given, read, ".")["valid"] is True
    )
    with pytest.raises(ValueError, match="unknown source_id"):
        read_covenant_fact(ReadCovenantFactInput("NOPE"))
    from decimal import Decimal

    from verifier.fixtures import RECORDS

    assert len(RECORDS) == 26 and len({r["source_id"] for r in RECORDS}) == 26
    assert all(r["metric"] != "Debt" or Decimal(r["value"]) >= 0 for r in RECORDS)
    row = company(
        "Equality Holdings",
        Classification.PASS,
        CovenantStatus.PASS,
        "2.00",
        ["EH-DEBT", "EH-EBITDA"],
        CovenantStatus.PASS,
        "5.00",
        ["EH-EBIT", "EH-INT"],
    )
    answer = ScreenCovenantsOutput(Classification.PASS, [row])
    assert check(args(["Equality Holdings"]), answer) == check(args(["Equality Holdings"]), answer)

import verifier
from contract import Classification, CompanyScreen, CovenantStatus, ScreenCovenantsInput, ScreenCovenantsOutput


def test_independent_expected_example():
    given = ScreenCovenantsInput(["Equality Holdings"], "FY2024", "2", "5")
    row = CompanyScreen(
        "Equality Holdings",
        Classification.PASS,
        CovenantStatus.PASS,
        "2.00",
        ["EH-DEBT", "EH-EBITDA"],
        CovenantStatus.PASS,
        "5.00",
        ["EH-EBIT", "EH-INT"],
        [],
    )
    assert (
        verifier.verify_task("screen-covenants", given, ScreenCovenantsOutput(Classification.PASS, [row]), None, ".")[
            "valid"
        ]
        is True
    )


def rejected(maximum="2", minimum="5"):
    given = ScreenCovenantsInput(["Equality Holdings"], "FY2024", maximum, minimum)
    made = ScreenCovenantsOutput(Classification.PASS, [])
    verdict = verifier.verify_task("screen-covenants", given, made, None, ".")
    assert verdict["valid"] is False
    assert verdict["score"] == 0.0
    assert "thresholds must be finite nonnegative ASCII decimals" in verdict["message"]


def test_independently_specified_nonfinite_and_negative_thresholds_are_rejected_without_crashing():
    for invalid in ("NaN", "sNaN", "Infinity", "-Infinity", "-0.01"):
        rejected(maximum=invalid)
        rejected(minimum=invalid)


def test_independently_specified_threshold_limits_are_enforced():
    for outside_limit in (
        "1000000000000000001",
        "0.0000000000000000001",
        "1e-19",
        "1" * 65,
    ):
        rejected(maximum=outside_limit)
        rejected(minimum=outside_limit)


def test_independently_specified_extreme_exponents_are_rejected_without_crashing():
    for extreme_exponent in ("1e999999999", "0e999999999", "0e-999999999"):
        rejected(maximum=extreme_exponent)
        rejected(minimum=extreme_exponent)

"""Typed declarations for covenant evidence and screening."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    LIST_COVENANT_FACTS = "list_covenant_facts"
    READ_COVENANT_FACT = "read_covenant_fact"


class Task(Enum):
    SCREEN_COVENANTS = "screen-covenants"


class Classification(Enum):
    PASS = "pass"
    FAIL = "fail"
    INSUFFICIENT_DATA = "insufficient_data"


class CovenantStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNEVALUABLE = "unevaluable"


class Reason(Enum):
    LEVERAGE_EXCEEDS_MAXIMUM = "leverage_exceeds_maximum"
    COVERAGE_BELOW_MINIMUM = "coverage_below_minimum"
    MISSING_DEBT = "missing_debt"
    MISSING_EBITDA = "missing_ebitda"
    NONPOSITIVE_EBITDA = "nonpositive_ebitda"
    MISSING_EBIT = "missing_ebit"
    MISSING_INTEREST_EXPENSE = "missing_interest_expense"
    NONPOSITIVE_INTEREST_EXPENSE = "nonpositive_interest_expense"


@dataclass
class ListCovenantFactsInput(Output):
    company: Annotated[str, "Exact fictional company; empty lists all"]


@dataclass
class CovenantFactMetadata(Output):
    source_id: Annotated[str, "Unique source ID"]
    company: Annotated[str, "Exact fictional company"]
    fiscal_year: Annotated[str, "Fiscal year"]
    metric: Annotated[str, "Debt, EBITDA, EBIT, or Interest expense"]
    currency: Annotated[str, "Currency"]
    unit_scale: Annotated[str, "Unit scale"]


@dataclass
class ListCovenantFactsOutput(Output):
    facts: Annotated[list[CovenantFactMetadata], "Value-free metadata"]


@dataclass
class ReadCovenantFactInput(Output):
    source_id: Annotated[str, "Listed source ID"]


@dataclass
class ReadCovenantFactOutput(Output):
    source_id: Annotated[str, "Requested source ID"]
    excerpt: Annotated[str, "Complete fictional covenant excerpt"]


@dataclass
class ScreenCovenantsInput(Output):
    companies: Annotated[list[str], "Nonempty unique exact fictional company names"]
    fiscal_year: Annotated[str, "Fiscal year"]
    maximum_leverage: Annotated[str, "Finite nonnegative decimal; max 64 chars, 1e18, exponent -18..18"]
    minimum_interest_coverage: Annotated[str, "Finite nonnegative decimal; max 64 chars, 1e18, exponent -18..18"]


@dataclass
class CompanyScreen(Output):
    company: Annotated[str, "Screened company"]
    classification: Annotated[Classification, "Company-level outcome"]
    leverage_status: Annotated[CovenantStatus, "Leverage covenant outcome"]
    leverage_ratio: Annotated[str, "Two-decimal display ratio or empty"]
    leverage_source_ids: Annotated[list[str], "Available debt and EBITDA sources in order"]
    coverage_status: Annotated[CovenantStatus, "Interest coverage covenant outcome"]
    interest_coverage_ratio: Annotated[str, "Two-decimal display ratio or empty"]
    coverage_source_ids: Annotated[list[str], "Available EBIT and interest sources in order"]
    reasons: Annotated[list[Reason], "Structured failure or insufficiency reasons"]


@dataclass
class ScreenCovenantsOutput(Output):
    overall: Annotated[Classification, "fail, else insufficient_data, else pass"]
    companies: Annotated[list[CompanyScreen], "One result per requested company, in input order"]


TOOLS = {
    Tool.LIST_COVENANT_FACTS: (ListCovenantFactsInput, ListCovenantFactsOutput),
    Tool.READ_COVENANT_FACT: (ReadCovenantFactInput, ReadCovenantFactOutput),
}
TASKS = {Task.SCREEN_COVENANTS: (ScreenCovenantsInput, ScreenCovenantsOutput)}

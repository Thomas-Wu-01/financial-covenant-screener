# Financial Covenant Screener

A closed-corpus NanoAgent task that screens lists of fictional companies against explicit leverage and interest-coverage thresholds. No facts describe real companies or loans.

## Tools

| Name | Purpose |
|---|---|
| `list_covenant_facts` | Lists value-free metadata for one exact company or the complete corpus. |
| `read_covenant_fact` | Reads one complete synthetic covenant fact. |
| `screen-covenants` | Agent task classifying every requested company and the overall list. |

Only two covenants are supported: leverage `debt / EBITDA <= maximum_leverage`, and interest coverage `EBIT / interest expense >= minimum_interest_coverage`. Inputs require a nonempty unique list of known companies, `FY2024`, and finite nonnegative ASCII decimal threshold strings. Each threshold is limited to 64 characters, a value of `1e18`, and a parsed decimal exponent from `-18` through `18`, inclusive; non-finite values and inputs outside these bounds are invalid. The exponent is checked before comparisons or other arithmetic. Facts normalize thousand and million scales to USD units.

Missing facts or nonpositive EBITDA/interest expense make that covenant `unevaluable`. Each company fails if an evaluable covenant fails; otherwise it is `insufficient_data` if either covenant is unevaluable; otherwise it passes. Overall is fail if any company fails, else insufficient if any is insufficient, else pass. Exact ratios are compared to thresholds before two-place `ROUND_HALF_UP` display rounding.

Example input: `{"companies":["Equality Holdings"],"fiscal_year":"FY2024","maximum_leverage":"2","minimum_interest_coverage":"5"}`

Expected output: `{"overall":"pass","companies":[{"company":"Equality Holdings","classification":"pass","leverage_status":"pass","leverage_ratio":"2.00","leverage_source_ids":["EH-DEBT","EH-EBITDA"],"coverage_status":"pass","interest_coverage_ratio":"5.00","coverage_source_ids":["EH-EBIT","EH-INT"],"reasons":[]}]}`

## Layout

The authoritative corpus has 26 fictional facts for seven boundary-focused companies. The verifier independently checks requested coverage and order, duplicates, evidence availability, citations, exact pre-rounding comparisons, structured reasons, company classifications, and overall precedence.

## Develop and run

In Ubuntu/WSL run `uv sync --extra dev --frozen`, `uv run --frozen pytest`, and `uv run --frozen ruff check .`; inspect with NanoAgent `plugin inspect`.

Limitations: FY2024 only, fixed exact identifiers, USD synthetic facts, two covenant formulas, no actual loan documents, and no proof of tool calls from correct citations alone.

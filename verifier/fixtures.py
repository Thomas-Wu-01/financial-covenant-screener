def fact(source_id, company, metric, value, unit_scale="million"):
    return {
        "source_id": source_id,
        "company": company,
        "fiscal_year": "FY2024",
        "metric": metric,
        "value": value,
        "currency": "USD",
        "unit_scale": unit_scale,
    }


COMPANIES = (
    "Equality Holdings",
    "High Leverage Co",
    "Low Coverage Co",
    "Missing Metrics Co",
    "Nonpositive Co",
    "Known Fail Missing Co",
    "Just Under Co",
)
RECORDS = (
    fact("EH-DEBT", COMPANIES[0], "Debt", "200"),
    fact("EH-EBITDA", COMPANIES[0], "EBITDA", "100"),
    fact("EH-EBIT", COMPANIES[0], "EBIT", "50"),
    fact("EH-INT", COMPANIES[0], "Interest expense", "10"),
    fact("HL-DEBT", COMPANIES[1], "Debt", "200010", "thousand"),
    fact("HL-EBITDA", COMPANIES[1], "EBITDA", "100"),
    fact("HL-EBIT", COMPANIES[1], "EBIT", "60"),
    fact("HL-INT", COMPANIES[1], "Interest expense", "10"),
    fact("LC-DEBT", COMPANIES[2], "Debt", "100"),
    fact("LC-EBITDA", COMPANIES[2], "EBITDA", "100"),
    fact("LC-EBIT", COMPANIES[2], "EBIT", "49999", "thousand"),
    fact("LC-INT", COMPANIES[2], "Interest expense", "10"),
    fact("MM-DEBT", COMPANIES[3], "Debt", "100"),
    fact("MM-EBITDA", COMPANIES[3], "EBITDA", "50"),
    fact("MM-EBIT", COMPANIES[3], "EBIT", "30"),
    fact("NP-DEBT", COMPANIES[4], "Debt", "100"),
    fact("NP-EBITDA", COMPANIES[4], "EBITDA", "0"),
    fact("NP-EBIT", COMPANIES[4], "EBIT", "20"),
    fact("NP-INT", COMPANIES[4], "Interest expense", "-1"),
    fact("KF-DEBT", COMPANIES[5], "Debt", "300"),
    fact("KF-EBITDA", COMPANIES[5], "EBITDA", "100"),
    fact("KF-EBIT", COMPANIES[5], "EBIT", "50"),
    fact("JU-DEBT", COMPANIES[6], "Debt", "199990", "thousand"),
    fact("JU-EBITDA", COMPANIES[6], "EBITDA", "100"),
    fact("JU-EBIT", COMPANIES[6], "EBIT", "50001", "thousand"),
    fact("JU-INT", COMPANIES[6], "Interest expense", "10"),
)
SCALES = {"thousand": "1000", "million": "1000000"}


def record_by_source(source_id):
    for row in RECORDS:
        if row["source_id"] == source_id:
            return row
    return None


def find(company, year, metric):
    for row in RECORDS:
        if row["company"] == company and row["fiscal_year"] == year and row["metric"] == metric:
            return row
    return None


def excerpt(row):
    return (
        "SYNTHETIC COVENANT FACT — fictional, not a real filing or loan record.\n"
        f"Source ID: {row['source_id']}\nCompany: {row['company']}\nFiscal year: {row['fiscal_year']}\n{row['metric']}: {row['value']} {row['currency']} {row['unit_scale']}\nCitation: {row['source_id']}"
    )

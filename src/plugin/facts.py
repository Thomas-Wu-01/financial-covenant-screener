from contract import CovenantFactMetadata, ListCovenantFactsOutput, ReadCovenantFactOutput
from verifier.fixtures import COMPANIES, RECORDS, excerpt, record_by_source


def list_covenant_facts(given):
    if given.company and given.company not in COMPANIES:
        raise ValueError("unknown company")
    rows = RECORDS if not given.company else tuple(r for r in RECORDS if r["company"] == given.company)
    return ListCovenantFactsOutput(
        [
            CovenantFactMetadata(
                r["source_id"], r["company"], r["fiscal_year"], r["metric"], r["currency"], r["unit_scale"]
            )
            for r in rows
        ]
    )


def read_covenant_fact(given):
    row = record_by_source(given.source_id)
    if row is None:
        raise ValueError(f"unknown source_id: {given.source_id}")
    return ReadCovenantFactOutput(given.source_id, excerpt(row))

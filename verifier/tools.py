from contract import CovenantFactMetadata

from .checks import result
from .fixtures import COMPANIES, RECORDS, excerpt, record_by_source


def metadata(row):
    return CovenantFactMetadata(
        row["source_id"], row["company"], row["fiscal_year"], row["metric"], row["currency"], row["unit_scale"]
    )


def verify_list_input(value):
    valid = not value.company or value.company in COMPANIES
    return result(valid, "input is valid" if valid else "unknown company")


def verify_list_output(given, made, workspace):
    rows = RECORDS if not given.company else tuple(r for r in RECORDS if r["company"] == given.company)
    valid = made.facts == [metadata(r) for r in rows]
    return result(valid, "metadata is complete" if valid else "metadata is incorrect")


def verify_read_input(value):
    valid = record_by_source(value.source_id) is not None
    return result(valid, "input is valid" if valid else "unknown source_id")


def verify_read_output(given, made, workspace):
    row = record_by_source(given.source_id)
    valid = row is not None and made.source_id == given.source_id and made.excerpt == excerpt(row)
    return result(valid, "fact is correct" if valid else "fact is incorrect")

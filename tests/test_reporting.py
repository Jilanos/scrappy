from zipfile import ZipFile

from scrappy.models import Offer, RankedOffer, ScoreResult
from scrappy.reporting import read_review_rows, write_xlsx


def test_writes_review_xlsx_with_all_scored_and_rejected_sheets(tmp_path) -> None:
    output = tmp_path / "report.xlsx"
    ranked = [
        RankedOffer(
            offer_id=12,
            offer=Offer(source="fixture", source_id="1", url="https://example.test", title="Engineer"),
            score=ScoreResult(score=80, eligible=True, location_status="paris", seniority_status="senior"),
            merged_sources=["fixture:1", "indeed_api:dup"],
            duplicate_reason="same normalized title/company/location",
        ),
        RankedOffer(
            offer_id=13,
            offer=Offer(source="fixture", source_id="2", url="https://example.test/no", title="Intern"),
            score=ScoreResult(score=0, eligible=False, location_status="paris", seniority_status="internship"),
        ),
    ]

    write_xlsx(output, ranked)

    assert output.exists()
    with ZipFile(output) as archive:
        assert "xl/worksheets/sheet1.xml" in archive.namelist()
        assert "xl/worksheets/sheet2.xml" in archive.namelist()
        workbook = archive.read("xl/workbook.xml").decode("utf-8")
        assert 'name="all_scored"' in workbook
        assert 'name="rejected"' in workbook

    rows = read_review_rows(output)
    assert rows[0]["offer_id"] == "12"
    assert rows[0]["merged_sources"] == "fixture:1; indeed_api:dup"
    assert rows[0]["duplicate_reason"] == "same normalized title/company/location"
    assert rows[0]["decision"] == ""
    assert rows[1]["source_id"] == "2"

    rejected_rows = read_review_rows(output, sheet_name="rejected")
    assert len(rejected_rows) == 1
    assert rejected_rows[0]["source_id"] == "2"

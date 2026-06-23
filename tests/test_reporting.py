from zipfile import ZipFile

from scrappy.models import Offer, RankedOffer, ScoreResult
from scrappy.reporting import write_xlsx


def test_writes_xlsx(tmp_path) -> None:
    output = tmp_path / "report.xlsx"
    ranked = [
        RankedOffer(
            offer=Offer(source="fixture", source_id="1", url="https://example.test", title="Engineer"),
            score=ScoreResult(score=80, eligible=True, location_status="paris", seniority_status="senior"),
        )
    ]

    write_xlsx(output, ranked)

    assert output.exists()
    with ZipFile(output) as archive:
        assert "xl/worksheets/sheet1.xml" in archive.namelist()

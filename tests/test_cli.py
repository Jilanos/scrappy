from scrappy.cli import main
from scrappy.models import Offer
from scrappy.reporting import HEADERS, _write_minimal_xlsx
from scrappy.storage import connect, create_run, init_db, iter_manual_reviews, upsert_offer


def test_import_reviews_command_persists_xlsx_decisions(tmp_path, capsys) -> None:
    db = tmp_path / "scrappy.sqlite"
    xlsx = tmp_path / "reviews.xlsx"
    offer = Offer(
        source="fixture",
        source_id="job-1",
        url="https://example.test/job-1",
        title="Engineer",
    )

    with connect(db) as conn:
        init_db(conn)
        run_id = create_run(conn, "fixture", 1)
        upsert_offer(conn, run_id, offer)

    row = [
        "1",
        "1",
        "fixture",
        "job-1",
        "selected",
        "top match",
        "2026-06-23T12:00:00+00:00",
        "92",
        "True",
        "Engineer",
        "",
        "Paris",
        "",
        "Full-Time",
        "paris",
        "confirmed",
        "https://example.test/job-1",
        "",
        "",
        "",
        "",
    ]
    _write_minimal_xlsx(xlsx, {"all_scored": [HEADERS, row], "rejected": [HEADERS]})

    main(["import-reviews", "--db", str(db), "--xlsx", str(xlsx)])

    captured = capsys.readouterr()
    with connect(db) as conn:
        rows = list(iter_manual_reviews(conn))

    assert "Imported reviews: 1" in captured.out
    assert rows[0]["decision"] == "selected"
    assert rows[0]["review_note"] == "top match"

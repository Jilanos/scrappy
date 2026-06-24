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

    values = {
        "rank": "1",
        "offer_id": "1",
        "source": "fixture",
        "source_id": "job-1",
        "decision": "selected",
        "review_note": "top match",
        "reviewed_at": "2026-06-23T12:00:00+00:00",
        "score": "92",
        "eligible": "True",
        "title": "Engineer",
        "location": "Paris",
        "contract_type": "Full-Time",
        "location_status": "paris",
        "seniority_status": "confirmed",
        "url": "https://example.test/job-1",
    }
    row = [values.get(header, "") for header in HEADERS]
    _write_minimal_xlsx(xlsx, {"all_scored": [HEADERS, row], "rejected": [HEADERS]})

    main(["import-reviews", "--db", str(db), "--xlsx", str(xlsx)])

    captured = capsys.readouterr()
    with connect(db) as conn:
        rows = list(iter_manual_reviews(conn))

    assert "Imported reviews: 1" in captured.out
    assert rows[0]["decision"] == "selected"
    assert rows[0]["review_note"] == "top match"


def test_run_continues_with_warning_when_indeed_provider_is_not_configured(tmp_path, capsys, monkeypatch) -> None:
    db = tmp_path / "scrappy.sqlite"
    xlsx = tmp_path / "out.xlsx"
    monkeypatch.delenv("SCRAPPY_INDEED_API_URL", raising=False)

    main(
        [
            "run",
            "--db",
            str(db),
            "--provider",
            "indeed-api",
            "--target-offers",
            "1",
            "--max-pages",
            "1",
            "--xlsx",
            str(xlsx),
        ]
    )

    captured = capsys.readouterr()

    assert "Provider: indeed_api" in captured.out
    assert "Warning: provider failed" in captured.out
    assert "SCRAPPY_INDEED_API_URL" in captured.out
    assert xlsx.exists()


def test_run_continues_with_warning_when_france_travail_is_not_configured(tmp_path, capsys, monkeypatch) -> None:
    db = tmp_path / "scrappy.sqlite"
    xlsx = tmp_path / "out.xlsx"
    monkeypatch.delenv("SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET", raising=False)

    main(
        [
            "run",
            "--db",
            str(db),
            "--provider",
            "france-travail",
            "--target-offers",
            "1",
            "--max-pages",
            "1",
            "--xlsx",
            str(xlsx),
        ]
    )

    captured = capsys.readouterr()

    assert "Provider: france_travail" in captured.out
    assert "Warning: provider failed" in captured.out
    assert "SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID" in captured.out
    assert xlsx.exists()

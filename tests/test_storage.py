from scrappy.models import Offer, ScoreResult
from scrappy.storage import connect, create_run, init_db, iter_manual_reviews, latest_ranked, save_analysis, save_manual_review, upsert_offer


def test_deduplicates_unchanged_offer(tmp_path) -> None:
    db = tmp_path / "scrappy.sqlite"
    offer = Offer(
        source="fixture",
        source_id="same",
        url="https://example.test/job",
        title="Engineer",
        description="Python electronics Paris",
    )

    with connect(db) as conn:
        init_db(conn)
        run_id = create_run(conn, "fixture", 1)
        offer_id, changed = upsert_offer(conn, run_id, offer)
        second_id, second_changed = upsert_offer(conn, run_id, offer)

    assert offer_id == second_id
    assert changed
    assert not second_changed


def test_saves_manual_review_by_stable_source_id(tmp_path) -> None:
    db = tmp_path / "scrappy.sqlite"
    offer = Offer(
        source="fixture",
        source_id="same",
        url="https://example.test/job",
        title="Engineer",
        description="Python electronics Paris",
    )

    with connect(db) as conn:
        init_db(conn)
        run_id = create_run(conn, "fixture", 1)
        upsert_offer(conn, run_id, offer)
        saved = save_manual_review(
            conn,
            source="fixture",
            source_id="same",
            decision="maybe",
            review_note="interesting scope",
            reviewed_at="2026-06-23T12:00:00+00:00",
        )
        rows = list(iter_manual_reviews(conn))

    assert saved
    assert len(rows) == 1
    assert rows[0]["decision"] == "maybe"
    assert rows[0]["review_note"] == "interesting scope"


def test_merges_cross_source_duplicates_by_normalized_title_company_location(tmp_path) -> None:
    db = tmp_path / "scrappy.sqlite"
    wttj_offer = Offer(
        source="wttj_algolia",
        source_id="wttj-1",
        url="https://wttj.example/job",
        title="Senior Electronics Engineer",
        company="Deeptech",
        location="Paris, France",
        contract_type="Full-Time",
        description="Signal processing electronics",
    )
    indeed_offer = Offer(
        source="indeed_api",
        source_id="indeed-1",
        url="https://indeed.example/job",
        title="Electronics Engineer",
        company="Deeptech",
        location="Paris",
        contract_type="Full-Time",
        description="Signal processing electronics",
    )

    with connect(db) as conn:
        init_db(conn)
        run_id = create_run(conn, "multi", 1)
        offer_id, _changed = upsert_offer(conn, run_id, wttj_offer)
        duplicate_id, duplicate_changed = upsert_offer(conn, run_id, indeed_offer)
        save_analysis(
            conn,
            run_id,
            offer_id,
            "test",
            ScoreResult(score=80, eligible=True, location_status="paris", seniority_status="confirmed"),
        )
        ranked = latest_ranked(conn, limit=None)

    assert duplicate_id == offer_id
    assert duplicate_changed
    assert ranked[0].merged_sources == ["wttj_algolia:wttj-1", "indeed_api:indeed-1"]
    assert ranked[0].duplicate_reason == "same normalized title/company/location"


def test_cross_source_duplicate_does_not_ping_pong_canonical_content(tmp_path) -> None:
    db = tmp_path / "scrappy.sqlite"
    wttj_offer = Offer(
        source="wttj_algolia",
        source_id="wttj-1",
        url="https://wttj.example/job",
        title="Senior Electronics Engineer",
        company="Deeptech",
        location="Paris, France",
        contract_type="Full-Time",
        description="Signal processing electronics",
    )
    indeed_offer = Offer(
        source="indeed_api",
        source_id="indeed-1",
        url="https://indeed.example/job",
        title="Electronics Engineer",
        company="Deeptech",
        location="Paris",
        contract_type="Full-Time",
        description="Signal processing electronics",
    )

    with connect(db) as conn:
        init_db(conn)
        run_id = create_run(conn, "multi", 1)
        offer_id, _ = upsert_offer(conn, run_id, wttj_offer)
        upsert_offer(conn, run_id, indeed_offer)
        second_run = create_run(conn, "multi", 1)
        _, wttj_changed_again = upsert_offer(conn, second_run, wttj_offer)
        _, indeed_changed_again = upsert_offer(conn, second_run, indeed_offer)
        row = conn.execute("SELECT title, url FROM offers WHERE id = ?", (offer_id,)).fetchone()

    assert not wttj_changed_again
    assert not indeed_changed_again
    assert row["title"] == "Senior Electronics Engineer"
    assert row["url"] == "https://wttj.example/job"

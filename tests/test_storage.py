from scrappy.models import Offer
from scrappy.storage import connect, create_run, init_db, iter_manual_reviews, save_manual_review, upsert_offer


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

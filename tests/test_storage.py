from scrappy.models import Offer
from scrappy.storage import connect, create_run, init_db, upsert_offer


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

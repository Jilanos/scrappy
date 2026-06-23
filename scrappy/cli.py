from __future__ import annotations

import argparse
from pathlib import Path

from scrappy.connectors import WttjPublicConnector
from scrappy.profile import load_profile, profile_terms
from scrappy.reporting import print_console, read_review_rows, write_xlsx
from scrappy.scoring import score_offer
from scrappy.storage import (
    connect,
    create_run,
    finish_run,
    init_db,
    iter_offers,
    latest_ranked,
    save_manual_review,
    save_analysis,
    upsert_offer,
)


DEFAULT_DB = "data/scrappy.sqlite"
DEFAULT_PROFILE = "examples/profile.yaml"
DEFAULT_REPORT = "reports/top_offers.xlsx"
DEFAULT_QUERIES = [
    "electronics engineer",
    "signal processing engineer",
    "R&D engineer",
    "medical imaging engineer",
]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="scrappy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help="Initialize or migrate the local SQLite database.")
    init_parser.add_argument("--db", default=DEFAULT_DB)

    run_parser = subparsers.add_parser("run", help="Collect, score, persist, and export a top shortlist.")
    run_parser.add_argument("--db", default=DEFAULT_DB)
    run_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    run_parser.add_argument("--provider", default="wttj-public", choices=["wttj-public"])
    run_parser.add_argument("--query", action="append", help="Override profile search query. Repeatable.")
    run_parser.add_argument("--max-pages", type=int, default=5)
    run_parser.add_argument("--target-offers", type=int, default=100)
    run_parser.add_argument("--hits-per-page", type=int, default=20)
    run_parser.add_argument("--top", type=int, default=5)
    run_parser.add_argument("--xlsx", default=DEFAULT_REPORT)

    rescore_parser = subparsers.add_parser("rescore", help="Rescore all stored offers with the current profile.")
    rescore_parser.add_argument("--db", default=DEFAULT_DB)
    rescore_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    rescore_parser.add_argument("--top", type=int, default=5)
    rescore_parser.add_argument("--xlsx", default=DEFAULT_REPORT)

    import_parser = subparsers.add_parser("import-reviews", help="Import manual XLSX review decisions.")
    import_parser.add_argument("--db", default=DEFAULT_DB)
    import_parser.add_argument("--xlsx", default=DEFAULT_REPORT)
    import_parser.add_argument("--sheet", default="all_scored")

    args = parser.parse_args(argv)
    if args.command == "init-db":
        _init_db(args.db)
    elif args.command == "run":
        _run(args)
    elif args.command == "rescore":
        _rescore(args)
    elif args.command == "import-reviews":
        _import_reviews(args)


def _init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        init_db(conn)
    print(f"Initialized database: {db_path}")


def _run(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    queries = args.query or _default_queries(profile)
    connector = WttjPublicConnector()

    with connect(args.db) as conn:
        init_db(conn)
        run_id = create_run(conn, connector.name, len(queries))
        offers = connector.discover(
            queries,
            max_pages=args.max_pages,
            target_count=args.target_offers,
            hits_per_page=args.hits_per_page,
        )
        changed_count = 0
        for offer in offers:
            offer_id, changed = upsert_offer(conn, run_id, offer)
            if changed:
                changed_count += 1
                save_analysis(conn, run_id, offer_id, _profile_version(profile), score_offer(offer, profile))
        finish_run(conn, run_id, discovered=len(offers), changed=changed_count)
        ranked = latest_ranked(conn, limit=None)

    print(f"Provider: {connector.name}")
    print(f"Discovered: {len(offers)}")
    print(f"New or changed: {changed_count}")
    print_console(ranked[: args.top])
    write_xlsx(args.xlsx, ranked)
    print(f"XLSX report: {args.xlsx}")


def _rescore(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    with connect(args.db) as conn:
        init_db(conn)
        run_id = create_run(conn, "rescore", 0)
        count = 0
        for offer_id, offer in iter_offers(conn):
            save_analysis(conn, run_id, offer_id, _profile_version(profile), score_offer(offer, profile))
            count += 1
        finish_run(conn, run_id, discovered=count, changed=count)
        ranked = latest_ranked(conn, limit=None)
    print(f"Rescored offers: {count}")
    print_console(ranked[: args.top])
    write_xlsx(args.xlsx, ranked)
    print(f"XLSX report: {args.xlsx}")


def _import_reviews(args: argparse.Namespace) -> None:
    rows = read_review_rows(args.xlsx, sheet_name=args.sheet)
    imported = 0
    skipped_empty = 0
    skipped_missing = 0
    with connect(args.db) as conn:
        init_db(conn)
        for row in rows:
            decision = row.get("decision", "").strip().lower()
            if not decision:
                skipped_empty += 1
                continue
            source = row.get("source", "").strip()
            source_id = row.get("source_id", "").strip()
            if not source or not source_id:
                skipped_missing += 1
                continue
            saved = save_manual_review(
                conn,
                source=source,
                source_id=source_id,
                decision=decision,
                review_note=row.get("review_note", ""),
                reviewed_at=row.get("reviewed_at", ""),
            )
            if saved:
                imported += 1
            else:
                skipped_missing += 1
    print(f"Imported reviews: {imported}")
    print(f"Skipped empty decisions: {skipped_empty}")
    print(f"Skipped missing offers: {skipped_missing}")


def _profile_version(profile: dict) -> str:
    return str(profile.get("version") or "unversioned")


def _default_queries(profile: dict) -> list[str]:
    queries = profile_terms(profile, "search", "default_queries")
    return queries or DEFAULT_QUERIES


if __name__ == "__main__":
    main()

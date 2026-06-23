from __future__ import annotations

import argparse
from pathlib import Path

from scrappy.connectors import WttjPublicConnector
from scrappy.profile import load_profile, profile_terms
from scrappy.reporting import print_console, write_xlsx
from scrappy.scoring import score_offer
from scrappy.storage import (
    connect,
    create_run,
    finish_run,
    init_db,
    iter_offers,
    latest_ranked,
    save_analysis,
    upsert_offer,
)


DEFAULT_DB = "data/scrappy.sqlite"
DEFAULT_PROFILE = "examples/profile.yaml"
DEFAULT_REPORT = "reports/top_offers.xlsx"


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
    run_parser.add_argument("--max-pages", type=int, default=1)
    run_parser.add_argument("--top", type=int, default=5)
    run_parser.add_argument("--xlsx", default=DEFAULT_REPORT)

    rescore_parser = subparsers.add_parser("rescore", help="Rescore all stored offers with the current profile.")
    rescore_parser.add_argument("--db", default=DEFAULT_DB)
    rescore_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    rescore_parser.add_argument("--top", type=int, default=5)
    rescore_parser.add_argument("--xlsx", default=DEFAULT_REPORT)

    args = parser.parse_args(argv)
    if args.command == "init-db":
        _init_db(args.db)
    elif args.command == "run":
        _run(args)
    elif args.command == "rescore":
        _rescore(args)


def _init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        init_db(conn)
    print(f"Initialized database: {db_path}")


def _run(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    queries = args.query or profile_terms(profile, "search", "target_roles")
    connector = WttjPublicConnector()

    with connect(args.db) as conn:
        init_db(conn)
        run_id = create_run(conn, connector.name, len(queries))
        offers = connector.discover(queries, max_pages=args.max_pages)
        changed_count = 0
        for offer in offers:
            offer_id, changed = upsert_offer(conn, run_id, offer)
            if changed:
                changed_count += 1
                save_analysis(conn, run_id, offer_id, _profile_version(profile), score_offer(offer, profile))
        finish_run(conn, run_id, discovered=len(offers), changed=changed_count)
        ranked = latest_ranked(conn, limit=args.top)

    print(f"Provider: {connector.name}")
    print(f"Discovered: {len(offers)}")
    print(f"New or changed: {changed_count}")
    print_console(ranked)
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
        ranked = latest_ranked(conn, limit=args.top)
    print(f"Rescored offers: {count}")
    print_console(ranked)
    write_xlsx(args.xlsx, ranked)
    print(f"XLSX report: {args.xlsx}")


def _profile_version(profile: dict) -> str:
    return str(profile.get("version") or "unversioned")


if __name__ == "__main__":
    main()

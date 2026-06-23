from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from scrappy.models import Offer, RankedOffer, ScoreResult


SCHEMA_VERSION = 1


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            provider TEXT NOT NULL,
            status TEXT NOT NULL,
            query_count INTEGER NOT NULL DEFAULT 0,
            discovered_count INTEGER NOT NULL DEFAULT 0,
            new_or_changed_count INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            url TEXT NOT NULL,
            canonical_url TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            remote TEXT NOT NULL,
            seniority TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            description TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            UNIQUE(source, source_id),
            UNIQUE(canonical_url)
        );

        CREATE TABLE IF NOT EXISTS source_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            offer_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            is_new_or_changed INTEGER NOT NULL,
            FOREIGN KEY(run_id) REFERENCES runs(id),
            FOREIGN KEY(offer_id) REFERENCES offers(id)
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            offer_id INTEGER NOT NULL,
            analyzed_at TEXT NOT NULL,
            profile_version TEXT NOT NULL,
            score INTEGER NOT NULL,
            eligible INTEGER NOT NULL,
            location_status TEXT NOT NULL,
            seniority_status TEXT NOT NULL,
            strengths_json TEXT NOT NULL,
            gaps_json TEXT NOT NULL,
            risks_json TEXT NOT NULL,
            reasons_json TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES runs(id),
            FOREIGN KEY(offer_id) REFERENCES offers(id)
        );
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
        (SCHEMA_VERSION, now_iso()),
    )
    conn.commit()


def create_run(conn: sqlite3.Connection, provider: str, query_count: int) -> int:
    cur = conn.execute(
        "INSERT INTO runs(started_at, provider, status, query_count) VALUES (?, ?, ?, ?)",
        (now_iso(), provider, "running", query_count),
    )
    conn.commit()
    return int(cur.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, discovered: int, changed: int, status: str = "done") -> None:
    conn.execute(
        "UPDATE runs SET status = ?, discovered_count = ?, new_or_changed_count = ? WHERE id = ?",
        (status, discovered, changed, run_id),
    )
    conn.commit()


def upsert_offer(conn: sqlite3.Connection, run_id: int, offer: Offer) -> tuple[int, bool]:
    content_hash = offer.content_hash or hash_offer(offer)
    canonical_url = canonicalize_url(offer.url)
    existing = conn.execute(
        "SELECT id, content_hash FROM offers WHERE source = ? AND source_id = ? OR canonical_url = ?",
        (offer.source, offer.source_id, canonical_url),
    ).fetchone()
    now = now_iso()
    changed = True
    if existing:
        offer_id = int(existing["id"])
        changed = existing["content_hash"] != content_hash
        if changed:
            conn.execute(
                """
                UPDATE offers
                SET title = ?, company = ?, location = ?, remote = ?, seniority = ?,
                    contract_type = ?, description = ?, content_hash = ?, last_seen_at = ?
                WHERE id = ?
                """,
                (
                    offer.title,
                    offer.company,
                    offer.location,
                    offer.remote,
                    offer.seniority,
                    offer.contract_type,
                    offer.description,
                    content_hash,
                    now,
                    offer_id,
                ),
            )
        else:
            conn.execute("UPDATE offers SET last_seen_at = ? WHERE id = ?", (now, offer_id))
    else:
        cur = conn.execute(
            """
            INSERT INTO offers(
                source, source_id, url, canonical_url, title, company, location, remote,
                seniority, contract_type, description, content_hash, first_seen_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                offer.source,
                offer.source_id,
                offer.url,
                canonical_url,
                offer.title,
                offer.company,
                offer.location,
                offer.remote,
                offer.seniority,
                offer.contract_type,
                offer.description,
                content_hash,
                now,
                now,
            ),
        )
        offer_id = int(cur.lastrowid)
    conn.execute(
        """
        INSERT INTO source_observations(run_id, offer_id, source, observed_at, content_hash, is_new_or_changed)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (run_id, offer_id, offer.source, now, content_hash, int(changed)),
    )
    conn.commit()
    return offer_id, changed


def save_analysis(
    conn: sqlite3.Connection,
    run_id: int,
    offer_id: int,
    profile_version: str,
    result: ScoreResult,
) -> None:
    conn.execute(
        """
        INSERT INTO analyses(
            run_id, offer_id, analyzed_at, profile_version, score, eligible,
            location_status, seniority_status, strengths_json, gaps_json, risks_json, reasons_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            offer_id,
            now_iso(),
            profile_version,
            result.score,
            int(result.eligible),
            result.location_status,
            result.seniority_status,
            json.dumps(result.strengths, ensure_ascii=False),
            json.dumps(result.gaps, ensure_ascii=False),
            json.dumps(result.risks, ensure_ascii=False),
            json.dumps(result.reasons, ensure_ascii=False),
        ),
    )
    conn.commit()


def latest_ranked(conn: sqlite3.Connection, limit: int = 5) -> list[RankedOffer]:
    rows = conn.execute(
        """
        SELECT o.*, a.score, a.eligible, a.location_status, a.seniority_status,
               a.strengths_json, a.gaps_json, a.risks_json, a.reasons_json
        FROM analyses a
        JOIN offers o ON o.id = a.offer_id
        WHERE a.id IN (SELECT MAX(id) FROM analyses GROUP BY offer_id)
        ORDER BY a.eligible DESC, a.score DESC, a.analyzed_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [_ranked_from_row(row) for row in rows]


def iter_offers(conn: sqlite3.Connection) -> Iterable[tuple[int, Offer]]:
    for row in conn.execute("SELECT * FROM offers ORDER BY id"):
        yield int(row["id"]), _offer_from_row(row)


def hash_offer(offer: Offer) -> str:
    payload = "\n".join(
        [
            offer.url,
            offer.title,
            offer.company,
            offer.location,
            offer.remote,
            offer.seniority,
            offer.contract_type,
            offer.description,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonicalize_url(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/")


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _offer_from_row(row: sqlite3.Row) -> Offer:
    return Offer(
        source=row["source"],
        source_id=row["source_id"],
        url=row["url"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        remote=row["remote"],
        seniority=row["seniority"],
        contract_type=row["contract_type"],
        description=row["description"],
        content_hash=row["content_hash"],
    )


def _ranked_from_row(row: sqlite3.Row) -> RankedOffer:
    return RankedOffer(
        offer=_offer_from_row(row),
        score=ScoreResult(
            score=int(row["score"]),
            eligible=bool(row["eligible"]),
            location_status=row["location_status"],
            seniority_status=row["seniority_status"],
            strengths=json.loads(row["strengths_json"]),
            gaps=json.loads(row["gaps_json"]),
            risks=json.loads(row["risks_json"]),
            reasons=json.loads(row["reasons_json"]),
        ),
    )

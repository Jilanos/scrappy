from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from scrappy.models import Offer, RankedOffer, ScoreResult


SCHEMA_VERSION = 3
VALID_DECISIONS = {"selected", "rejected", "maybe"}


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
            dedupe_key TEXT NOT NULL DEFAULT '',
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

        CREATE TABLE IF NOT EXISTS offer_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            url TEXT NOT NULL,
            duplicate_reason TEXT NOT NULL DEFAULT '',
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            FOREIGN KEY(offer_id) REFERENCES offers(id),
            UNIQUE(source, source_id)
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

        CREATE TABLE IF NOT EXISTS manual_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            decision TEXT NOT NULL CHECK(decision IN ('selected', 'rejected', 'maybe')),
            review_note TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL,
            imported_at TEXT NOT NULL,
            FOREIGN KEY(offer_id) REFERENCES offers(id),
            UNIQUE(source, source_id)
        );
        """
    )
    _ensure_column(conn, "offers", "dedupe_key", "TEXT NOT NULL DEFAULT ''")
    _backfill_dedupe_keys(conn)
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
    dedupe_key = offer_dedupe_key(offer)
    existing = conn.execute(
        """
        SELECT id, content_hash FROM offers
        WHERE (source = ? AND source_id = ?)
           OR canonical_url = ?
           OR (dedupe_key != '' AND dedupe_key = ?)
           OR id IN (SELECT offer_id FROM offer_aliases WHERE source = ? AND source_id = ?)
        """,
        (offer.source, offer.source_id, canonical_url, dedupe_key, offer.source, offer.source_id),
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
                    contract_type = ?, description = ?, content_hash = ?, dedupe_key = ?, last_seen_at = ?
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
                    dedupe_key,
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
                seniority, contract_type, description, content_hash, first_seen_at, last_seen_at, dedupe_key
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                dedupe_key,
            ),
        )
        offer_id = int(cur.lastrowid)
    save_offer_alias(conn, offer_id, offer, duplicate_reason(offer, offer_id, conn))
    conn.execute(
        """
        INSERT INTO source_observations(run_id, offer_id, source, observed_at, content_hash, is_new_or_changed)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (run_id, offer_id, offer.source, now, content_hash, int(changed)),
    )
    conn.commit()
    return offer_id, changed


def save_offer_alias(conn: sqlite3.Connection, offer_id: int, offer: Offer, duplicate_reason: str = "") -> None:
    now = now_iso()
    conn.execute(
        """
        INSERT INTO offer_aliases(offer_id, source, source_id, url, duplicate_reason, first_seen_at, last_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, source_id) DO UPDATE SET
            offer_id = excluded.offer_id,
            url = excluded.url,
            duplicate_reason = excluded.duplicate_reason,
            last_seen_at = excluded.last_seen_at
        """,
        (offer_id, offer.source, offer.source_id, offer.url, duplicate_reason, now, now),
    )


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


def latest_ranked(conn: sqlite3.Connection, limit: int | None = 5) -> list[RankedOffer]:
    limit_sql = ""
    params: tuple[int, ...] = ()
    if limit is not None:
        limit_sql = "LIMIT ?"
        params = (limit,)
    rows = conn.execute(
        f"""
        SELECT o.*, o.id AS offer_id, a.score, a.eligible, a.location_status, a.seniority_status,
               a.strengths_json, a.gaps_json, a.risks_json, a.reasons_json
        FROM analyses a
        JOIN offers o ON o.id = a.offer_id
        WHERE a.id IN (SELECT MAX(id) FROM analyses GROUP BY offer_id)
        ORDER BY a.eligible DESC, a.score DESC, a.analyzed_at DESC
        {limit_sql}
        """,
        params,
    ).fetchall()
    ranked = []
    for row in rows:
        offer_id = int(row["offer_id"])
        merged_sources, reason = offer_alias_summary(conn, offer_id)
        ranked.append(_ranked_from_row(row, merged_sources=merged_sources, duplicate_reason=reason))
    return ranked


def save_manual_review(
    conn: sqlite3.Connection,
    source: str,
    source_id: str,
    decision: str,
    review_note: str = "",
    reviewed_at: str | None = None,
) -> bool:
    normalized_decision = decision.strip().lower()
    if normalized_decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision: {decision}")

    row = conn.execute(
        "SELECT id FROM offers WHERE source = ? AND source_id = ?",
        (source, source_id),
    ).fetchone()
    if row is None:
        return False

    now = now_iso()
    conn.execute(
        """
        INSERT INTO manual_reviews(
            offer_id, source, source_id, decision, review_note, reviewed_at, imported_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, source_id) DO UPDATE SET
            offer_id = excluded.offer_id,
            decision = excluded.decision,
            review_note = excluded.review_note,
            reviewed_at = excluded.reviewed_at,
            imported_at = excluded.imported_at
        """,
        (
            int(row["id"]),
            source,
            source_id,
            normalized_decision,
            review_note.strip(),
            reviewed_at.strip() if reviewed_at else now,
            now,
        ),
    )
    conn.commit()
    return True


def iter_manual_reviews(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    yield from conn.execute("SELECT * FROM manual_reviews ORDER BY imported_at DESC, id DESC")


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


def offer_dedupe_key(offer: Offer) -> str:
    title = _normalize_for_dedupe(offer.title)
    company = _normalize_for_dedupe(offer.company)
    location = _normalize_location_for_dedupe(offer.location)
    if not title or not company:
        return ""
    return hashlib.sha256(f"{title}|{company}|{location}".encode("utf-8")).hexdigest()


def duplicate_reason(offer: Offer, offer_id: int, conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT source, source_id FROM offers WHERE id = ?", (offer_id,)).fetchone()
    if row is None:
        return ""
    if row["source"] == offer.source and row["source_id"] == offer.source_id:
        return ""
    return "same normalized title/company/location"


def offer_alias_summary(conn: sqlite3.Connection, offer_id: int) -> tuple[list[str], str]:
    rows = conn.execute(
        """
        SELECT source, source_id, duplicate_reason
        FROM offer_aliases
        WHERE offer_id = ?
        ORDER BY first_seen_at, id
        """,
        (offer_id,),
    ).fetchall()
    sources = [f"{row['source']}:{row['source_id']}" for row in rows]
    reasons = [row["duplicate_reason"] for row in rows if row["duplicate_reason"]]
    return sources, "; ".join(dict.fromkeys(reasons))


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


def _ranked_from_row(
    row: sqlite3.Row,
    merged_sources: list[str] | None = None,
    duplicate_reason: str = "",
) -> RankedOffer:
    merged_sources_json = row["merged_sources_json"] if "merged_sources_json" in row.keys() else "[]"
    duplicate_reason_text = row["duplicate_reason"] if "duplicate_reason" in row.keys() else ""
    sources = merged_sources if merged_sources is not None else json.loads(merged_sources_json)
    return RankedOffer(
        offer=_offer_from_row(row),
        offer_id=int(row["offer_id"]) if "offer_id" in row.keys() else None,
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
        merged_sources=sources,
        duplicate_reason=duplicate_reason or duplicate_reason_text or "",
    )


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _backfill_dedupe_keys(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT * FROM offers WHERE dedupe_key = ''").fetchall()
    for row in rows:
        conn.execute(
            "UPDATE offers SET dedupe_key = ? WHERE id = ?",
            (offer_dedupe_key(_offer_from_row(row)), int(row["id"])),
        )


def _normalize_for_dedupe(value: str) -> str:
    text = value.lower()
    text = re.sub(r"\b(?:h/f|f/h|m/w|w/m|f/m|m/f|cdi|senior|confirmed|junior)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_location_for_dedupe(value: str) -> str:
    text = value.lower()
    if "paris" in text:
        return "paris"
    return _normalize_for_dedupe(text)

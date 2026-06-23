from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Offer:
    source: str
    source_id: str
    url: str
    title: str
    company: str = ""
    location: str = ""
    remote: str = ""
    seniority: str = ""
    contract_type: str = ""
    description: str = ""
    content_hash: str = ""


@dataclass(frozen=True)
class ScoreResult:
    score: int
    eligible: bool
    location_status: str
    seniority_status: str
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RankedOffer:
    offer: Offer
    score: ScoreResult

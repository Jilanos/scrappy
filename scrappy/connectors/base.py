from __future__ import annotations

from dataclasses import dataclass

from scrappy.models import Offer


@dataclass(frozen=True)
class SearchPage:
    offers: list[Offer]
    query: str
    page: int
    hits: int
    nb_hits: int
    nb_pages: int


@dataclass(frozen=True)
class DiscoveryResult:
    provider: str
    offers: list[Offer]
    pages: list[SearchPage]
    raw_hits: int
    duplicate_hits: int
    target_reached: bool
    error: str = ""

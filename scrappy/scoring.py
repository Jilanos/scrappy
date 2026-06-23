from __future__ import annotations

import re
from collections.abc import Iterable

from scrappy.models import Offer, ScoreResult
from scrappy.profile import profile_terms


SUPPORT_ONLY_PRIMARY_SKILLS = {"python"}


def score_offer(offer: Offer, profile: dict) -> ScoreResult:
    text = _offer_text(offer)
    location_status, location_ok = _location_status(offer)
    contract_status, contract_ok = _contract_status(text)
    exclusion = _hard_exclusion(text)
    if exclusion:
        return ScoreResult(
            score=0,
            eligible=False,
            location_status=location_status,
            seniority_status="excluded",
            gaps=[exclusion],
            risks=[exclusion],
            reasons=[exclusion],
        )

    seniority_status, seniority_points, seniority_ok = _seniority_score(offer)
    primary = profile_terms(profile, "skills", "primary")
    secondary = profile_terms(profile, "skills", "secondary")
    role_terms = profile_terms(profile, "search", "target_roles")

    primary_hits = _matched_terms(text, primary)
    secondary_hits = _matched_terms(text, secondary)
    role_hits = _matched_terms(text, role_terms)

    score = 0
    strengths: list[str] = []
    gaps: list[str] = []
    risks: list[str] = []
    reasons: list[str] = []

    if location_ok:
        score += 30
        strengths.append(f"location: {location_status}")
    else:
        gaps.append(f"location not eligible: {offer.location or offer.remote or 'unknown'}")
    if contract_ok:
        strengths.append(f"contract: {contract_status}")
    else:
        gaps.append(f"contract not eligible: {offer.contract_type or 'unknown'}")

    score += min(30, len(primary_hits) * 6)
    score += min(15, len(secondary_hits) * 3)
    score += min(10, len(role_hits) * 3)
    score += seniority_points

    if primary_hits:
        strengths.append("primary skills: " + ", ".join(primary_hits[:6]))
    else:
        gaps.append("no primary skill match")
    if primary_hits and not _domain_primary_hits(primary_hits):
        gaps.append("no domain primary skill match")
    if secondary_hits:
        strengths.append("secondary skills: " + ", ".join(secondary_hits[:5]))
    if role_hits:
        strengths.append("role terms: " + ", ".join(role_hits[:4]))
    if not seniority_ok:
        gaps.append(f"seniority not target: {seniority_status}")
    else:
        strengths.append(f"seniority: {seniority_status}")

    if _contains_any(text, profile_terms(profile, "exclusions", "downrank_terms")):
        score -= 15
        risks.append("ESN/consulting signal")
    if _contains_any(text, ["salary", "salaire", "compensation"]):
        reasons.append("salary metadata present")
    else:
        reasons.append("salary not used as a primary criterion")

    skill_ok = bool(_domain_primary_hits(primary_hits))
    eligible = location_ok and seniority_ok and contract_ok and skill_ok
    if not eligible:
        score = min(score, 49)

    return ScoreResult(
        score=max(0, min(100, score)),
        eligible=eligible,
        location_status=location_status,
        seniority_status=seniority_status,
        strengths=strengths,
        gaps=gaps,
        risks=risks,
        reasons=reasons,
    )


def _offer_text(offer: Offer) -> str:
    return " ".join(
        [
            offer.title,
            offer.company,
            offer.location,
            offer.remote,
            offer.seniority,
            offer.contract_type,
            offer.description,
        ]
    ).lower()


def _location_status(offer: Offer) -> tuple[str, bool]:
    location_text = " ".join([offer.location, offer.remote]).lower()
    remote_text = " ".join([offer.remote, offer.description]).lower()
    if _contains_any(remote_text, ["full remote", "fully remote", "remote first", "remote-first", "100% remote"]):
        return "full remote", True
    if re.search(r"\bparis\b", location_text):
        return "paris intramuros", True
    if _contains_any(location_text, ["remote", "hybrid", "teletravail"]):
        return "remote unclear", False
    return "not paris or full remote", False


def _contract_status(text: str) -> tuple[str, bool]:
    if _contains_any(text, ["cdi", "full-time", "full time", "permanent", "temps plein"]):
        return "cdi/full-time", True
    if _contains_any(text, ["internship", "apprenticeship", "alternance", "stage", "freelance", "part-time", "part time", "temporary"]):
        return "non-target contract", False
    return "unknown", False


def _seniority_score(offer: Offer) -> tuple[str, int, bool]:
    text = _offer_text(offer)
    title_text = offer.title.lower()
    if _contains_any(text, ["internship", "intern ", "stage", "apprenticeship", "alternance", "work-study"]):
        return "internship/apprenticeship", 0, False
    if _contains_any(text, ["junior", "entry level", "entry-level", "graduate"]):
        return "junior", 0, False
    if _max_required_years(text) > 6:
        return "too_senior_gt_6_years", 0, False
    if _contains_any(title_text, ["head of", "lead", "principal", "staff", "director", "manager"]):
        return "too_senior_leadership", 0, False
    if _contains_any(text, ["senior"]):
        return "senior_plus", 15, True
    if _contains_any(text, ["confirmed", "confirme", "experienced", "mid-level", "mid level"]):
        return "confirmed", 12, True
    return "unspecified", 6, True


def _max_required_years(text: str) -> int:
    years = []
    patterns = [
        r"(\d{1,2})\s*\+?\s*(?:years?|ans)\s+(?:of\s+)?experience",
        r"(?:experience|exp[. ]*)\s*(?:of\s*)?(\d{1,2})\s*\+?\s*(?:years?|ans)",
        r"(?:minimum|min\.?|at least|au moins)\s*(\d{1,2})\s*\+?\s*(?:years?|ans)",
    ]
    for pattern in patterns:
        years.extend(int(match) for match in re.findall(pattern, text))
    return max(years, default=0)


def _hard_exclusion(text: str) -> str | None:
    if _contains_any(text, ["internship", "apprenticeship", "alternance", "work-study"]):
        return "excluded internship/apprenticeship"
    military = _contains_any(text, ["military", "defense", "defence", "army", "navy", "air force", "armement", "militaire"])
    adjacent = _contains_any(text, ["detection", "sensing", "imaging", "safety", "security"])
    if military and not adjacent:
        return "excluded direct military role"
    return None


def _matched_terms(text: str, terms: Iterable[str]) -> list[str]:
    hits = []
    for term in terms:
        normalized = str(term).strip().lower()
        if normalized and normalized in text:
            hits.append(str(term))
    return hits


def _domain_primary_hits(primary_hits: Iterable[str]) -> list[str]:
    return [
        hit
        for hit in primary_hits
        if hit.strip().lower() not in SUPPORT_ONLY_PRIMARY_SKILLS
    ]


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(str(term).lower() in text for term in terms)

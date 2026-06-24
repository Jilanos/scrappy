"""Skill-gap ("boost") analysis.

Answers the question: *which skills, if added to my profile, would boost my CV the
most against the offers already collected?*

The approach is deterministic and reuses the existing scoring engine. For each
candidate skill, the profile is hypothetically augmented with that skill and every
stored offer is re-scored. The marginal value of a skill is then the aggregate of:

- ``offers_unlocked``: offers that flip from non-eligible to eligible, i.e. offers
  blocked *only* by the missing domain-skill gate. This is the strongest signal and
  matches the user's request to surface offers that "could be scored much higher if a
  key skill appeared in the profile";
- ``offers_boosted``: offers whose score increases at all;
- ``total_score_gain`` / ``avg_score_gain``: how much raw score the skill adds.

A skill only moves the needle on an offer that actually mentions it, because matching
is the intersection of profile terms and offer text. Offers blocked by location,
contract or seniority gates are never unlocked by a skill alone, which keeps the
recommendation honest.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Iterable

from scrappy.models import Offer
from scrappy.profile import profile_terms
from scrappy.scoring import score_offer


@dataclass(frozen=True)
class SkillBoost:
    skill: str
    offers_unlocked: int
    offers_boosted: int
    total_score_gain: int
    avg_score_gain: float
    example_offers: list[str] = field(default_factory=list)


def candidate_skills(profile: dict) -> list[str]:
    """Return declared growth skills that are not already part of the profile."""

    declared = profile_terms(profile, "growth", "candidate_skills")
    existing = {skill.strip().lower() for skill in _all_profile_skills(profile)}
    seen: set[str] = set()
    candidates: list[str] = []
    for skill in declared:
        key = skill.strip().lower()
        if not key or key in existing or key in seen:
            continue
        seen.add(key)
        candidates.append(skill)
    return candidates


def augment_profile(profile: dict, skill: str) -> dict:
    """Return a deep copy of ``profile`` with ``skill`` added as a primary skill."""

    augmented = copy.deepcopy(profile)
    skills = augmented.get("skills")
    if not isinstance(skills, dict):
        skills = {}
        augmented["skills"] = skills
    primary = list(skills.get("primary") or [])
    primary.append(skill)
    skills["primary"] = primary
    return augmented


def skill_boosts(
    offers: Iterable[Offer],
    profile: dict,
    candidates: list[str] | None = None,
    max_examples: int = 5,
) -> list[SkillBoost]:
    """Rank candidate skills by their marginal value across ``offers``."""

    skills = candidate_skills(profile) if candidates is None else candidates
    offer_list = list(offers)
    baseline = [score_offer(offer, profile) for offer in offer_list]

    boosts: list[SkillBoost] = []
    for skill in skills:
        augmented = augment_profile(profile, skill)
        unlocked = 0
        boosted = 0
        total_gain = 0
        examples: list[str] = []
        for offer, base in zip(offer_list, baseline):
            result = score_offer(offer, augmented)
            gain = result.score - base.score
            became_eligible = result.eligible and not base.eligible
            if gain > 0 or became_eligible:
                boosted += 1
                total_gain += max(0, gain)
                if len(examples) < max_examples:
                    examples.append(offer.title or offer.url)
            if became_eligible:
                unlocked += 1
        if boosted == 0 and unlocked == 0:
            continue
        avg = round(total_gain / boosted, 1) if boosted else 0.0
        boosts.append(
            SkillBoost(
                skill=skill,
                offers_unlocked=unlocked,
                offers_boosted=boosted,
                total_score_gain=total_gain,
                avg_score_gain=avg,
                example_offers=examples,
            )
        )

    boosts.sort(
        key=lambda b: (b.offers_unlocked, b.total_score_gain, b.offers_boosted),
        reverse=True,
    )
    return boosts


def _all_profile_skills(profile: dict) -> list[str]:
    return profile_terms(profile, "skills", "primary") + profile_terms(profile, "skills", "secondary")

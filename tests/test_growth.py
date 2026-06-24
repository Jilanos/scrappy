from scrappy.growth import augment_profile, candidate_skills, skill_boosts
from scrappy.models import Offer


def _base_profile() -> dict:
    return {
        "version": "test",
        "skills": {
            "primary": ["signal processing"],
            "secondary": ["python"],
        },
        "growth": {
            "candidate_skills": ["fpga", "machine learning", "signal processing"],
        },
    }


def _eligible_offer(source_id: str, description: str) -> Offer:
    return Offer(
        source="fixture",
        source_id=source_id,
        url=f"https://example.test/{source_id}",
        title="Confirmed Engineer",
        company="Deeptech",
        location="Paris",
        seniority="confirmed",
        contract_type="Full-Time",
        description=description,
    )


def test_candidate_skills_drops_skills_already_in_profile() -> None:
    candidates = candidate_skills(_base_profile())
    # "signal processing" is already a primary skill and must be filtered out.
    assert "signal processing" not in [c.lower() for c in candidates]
    assert {c.lower() for c in candidates} == {"fpga", "machine learning"}


def test_augment_profile_does_not_mutate_original() -> None:
    profile = _base_profile()
    augmented = augment_profile(profile, "fpga")
    assert "fpga" in [s.lower() for s in augmented["skills"]["primary"]]
    assert "fpga" not in [s.lower() for s in profile["skills"]["primary"]]


def test_skill_unlocks_offer_blocked_only_by_missing_skill() -> None:
    profile = _base_profile()
    # Offer is Paris/CDI/confirmed but only mentions FPGA, so the baseline profile
    # (primary: signal processing) has no domain skill match and rejects it.
    offer = _eligible_offer("fpga-1", "We build FPGA pipelines for hardware systems.")

    boosts = skill_boosts([offer], profile)
    by_skill = {b.skill.lower(): b for b in boosts}

    assert "fpga" in by_skill
    assert by_skill["fpga"].offers_unlocked == 1
    assert by_skill["fpga"].offers_boosted == 1
    assert by_skill["fpga"].example_offers


def test_skill_with_no_matching_offer_is_omitted() -> None:
    profile = _base_profile()
    offer = _eligible_offer("fpga-2", "We build FPGA pipelines for hardware systems.")

    boosts = skill_boosts([offer], profile)
    by_skill = {b.skill.lower(): b for b in boosts}

    # No offer mentions machine learning, so it cannot boost anything.
    assert "machine learning" not in by_skill


def test_boosts_sorted_by_unlocks_then_total_gain() -> None:
    profile = _base_profile()
    offers = [
        _eligible_offer("fpga-a", "FPGA design role."),
        _eligible_offer("fpga-b", "Another FPGA heavy position."),
        _eligible_offer("ml-a", "Machine learning research, but internship only."),
    ]
    # The ML offer mentions "internship" -> hard-excluded -> ML cannot unlock it.
    boosts = skill_boosts(offers, profile)

    assert boosts, "expected at least one impactful skill"
    assert boosts[0].skill.lower() == "fpga"
    assert boosts[0].offers_unlocked == 2

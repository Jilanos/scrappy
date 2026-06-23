from scrappy.models import Offer
from scrappy.profile import load_profile
from scrappy.scoring import score_offer


def test_scores_relevant_paris_confirmed_offer() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="1",
        url="https://example.test/job",
        title="Senior Electronics and Signal Processing Engineer",
        company="Deeptech",
        location="Paris",
        seniority="Senior",
        description="Python FPGA ultrasound medical imaging prototype validation",
    )

    result = score_offer(offer, profile)

    assert result.eligible
    assert result.score >= 70
    assert "paris" in result.location_status


def test_excludes_internship() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="2",
        url="https://example.test/internship",
        title="Electronics internship",
        company="Deeptech",
        location="Paris",
        description="Internship in signal processing",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.score == 0
    assert "internship" in " ".join(result.gaps)


def test_rejects_unclear_remote_outside_paris() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="3",
        url="https://example.test/hybrid",
        title="Confirmed FPGA Engineer",
        company="Tech",
        location="Lyon",
        remote="hybrid",
        seniority="confirmed",
        description="Python FPGA electronics",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.location_status == "remote unclear"

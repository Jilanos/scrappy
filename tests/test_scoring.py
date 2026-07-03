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
        contract_type="Full-Time",
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
        contract_type="Full-Time",
        description="Python FPGA electronics",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.location_status == "remote unclear"


def test_accepts_substantial_remote_hybrid_outside_paris() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="3b",
        url="https://example.test/substantial-hybrid",
        title="Confirmed Electronics Engineer",
        company="Tech",
        location="Lyon",
        remote="Hybrid",
        seniority="confirmed",
        contract_type="Full-Time",
        description="Electronics and signal processing role with 3 days remote per week.",
    )

    result = score_offer(offer, profile)

    assert result.eligible
    assert result.location_status == "substantial remote hybrid"


def test_rejects_missing_cdi_or_full_time_contract() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="4",
        url="https://example.test/job",
        title="Confirmed Electronics Engineer",
        company="Deeptech",
        location="Paris",
        seniority="confirmed",
        description="Python electronics signal processing",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert "contract not eligible" in " ".join(result.gaps)


def test_rejects_non_paris_offer_even_when_description_mentions_paris() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="5",
        url="https://example.test/job",
        title="Confirmed Electronics Engineer",
        company="Deeptech",
        location="Grenoble, France",
        seniority="confirmed",
        contract_type="Full-Time",
        description="The team works with the Paris HQ on signal processing and electronics.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.location_status == "not paris or full remote"


def test_rejects_roles_requiring_more_than_six_years() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="6",
        url="https://example.test/job",
        title="Senior Electronics Engineer",
        company="Deeptech",
        location="Paris",
        seniority="senior",
        contract_type="Full-Time",
        description="Requires 7+ years of experience in electronics and signal processing.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.seniority_status == "too_senior_gt_6_years"


def test_rejects_leadership_titles_as_too_senior() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="7",
        url="https://example.test/job",
        title="Lead Electronics Engineer",
        company="Deeptech",
        location="Paris",
        seniority="senior",
        contract_type="Full-Time",
        description="Electronics and signal processing role.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.seniority_status == "too_senior_leadership"


def test_rejects_offer_without_primary_skill_match() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="8",
        url="https://example.test/job",
        title="Operations Engineer",
        company="Saas",
        location="Paris",
        seniority="confirmed",
        contract_type="Full-Time",
        description="Customer operations and process automation.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert "no primary skill match" in " ".join(result.gaps)


def test_accepts_accented_french_telework_offer_outside_paris() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="10",
        url="https://example.test/job",
        title="Ingénieur électronique confirmé",
        company="Deeptech",
        location="Lyon",
        remote="Hybride",
        contract_type="CDI",
        description="Instrumentation et FPGA, 4 jours de télétravail par semaine.",
    )

    result = score_offer(offer, profile)

    assert result.eligible
    assert result.location_status == "substantial remote hybrid"
    assert result.seniority_status == "confirmed"


def test_rejects_french_offer_requiring_more_than_six_years() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="11",
        url="https://example.test/job",
        title="Ingénieur traitement du signal",
        company="Deeptech",
        location="Paris",
        contract_type="CDI",
        description="Vous justifiez de 7 ans d'expérience en électronique et traitement du signal.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert result.seniority_status == "too_senior_gt_6_years"


def test_hard_exclusion_terms_come_from_profile() -> None:
    profile = load_profile("examples/profile.yaml")
    profile["exclusions"]["military_terms"] = ["weapons systems"]
    profile["exclusions"]["allowed_adjacent_terms"] = ["imaging"]
    offer = Offer(
        source="fixture",
        source_id="12",
        url="https://example.test/job",
        title="Confirmed Electronics Engineer",
        company="Deeptech",
        location="Paris",
        contract_type="Full-Time",
        description="Signal processing for weapons systems.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert "excluded direct military role" in " ".join(result.reasons)


def test_rejects_python_only_skill_match() -> None:
    profile = load_profile("examples/profile.yaml")
    offer = Offer(
        source="fixture",
        source_id="9",
        url="https://example.test/job",
        title="Senior Data Engineer",
        company="Saas",
        location="Paris",
        seniority="senior",
        contract_type="Full-Time",
        description="Python pipelines and analytics platform.",
    )

    result = score_offer(offer, profile)

    assert not result.eligible
    assert "no domain primary skill match" in " ".join(result.gaps)

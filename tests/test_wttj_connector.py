from scrappy.connectors.wttj import WttjPublicConnector


def test_parses_wttj_job_links_from_html() -> None:
    html = """
    <a href="/en/companies/acme/jobs/senior-electronics-engineer_paris">
      Senior Electronics Engineer Acme Paris
    </a>
    """

    offers = WttjPublicConnector().parse_search_html(html, source_url="fixture")

    assert len(offers) == 1
    assert offers[0].source_id == "acme:senior-electronics-engineer_paris"
    assert offers[0].url.endswith("/en/companies/acme/jobs/senior-electronics-engineer_paris")


def test_maps_algolia_hit_to_offer() -> None:
    hit = {
        "objectID": "123",
        "slug": "electronics-engineer_paris",
        "name": "Electronics Engineer",
        "profile": "Python FPGA signal processing",
        "organization": {"name": "Deeptech", "slug": "deeptech"},
        "office": {"city": "Paris", "country": "France"},
        "remote": "partial",
        "experience_level_minimum": 5,
        "contract_type_names": {"en": "Full-Time"},
    }

    offer = WttjPublicConnector().offer_from_hit(hit)

    assert offer.source == "wttj_algolia"
    assert offer.source_id == "123"
    assert offer.title == "Electronics Engineer"
    assert offer.company == "Deeptech"
    assert offer.location == "Paris, France"
    assert offer.seniority == "senior"
    assert offer.contract_type == "Full-Time"

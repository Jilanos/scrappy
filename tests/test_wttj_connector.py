from scrappy.connectors.wttj import WttjPublicConnector
from scrappy.models import Offer


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


def test_discover_paginates_until_target_count() -> None:
    class FixtureConnector(WttjPublicConnector):
        def search_page(self, query: str, page: int = 0, hits_per_page: int = 20, retries: int = 2):
            from scrappy.connectors.wttj import SearchPage

            offers = [
                Offer(
                    source=self.name,
                    source_id=f"{query}-{page}-{index}",
                    url=f"https://example.test/{query}/{page}/{index}",
                    title="Engineer",
                )
                for index in range(2)
            ]
            return SearchPage(offers=offers, query=query, page=page, hits=len(offers), nb_hits=6, nb_pages=3)

    offers = FixtureConnector().discover(["electronics", "signal"], max_pages=3, target_count=5)

    assert len(offers) == 6
    assert offers[0].source_id == "electronics-0-0"
    assert offers[2].source_id == "signal-0-0"
    assert offers[-1].source_id == "electronics-1-1"


def test_discover_with_stats_reports_raw_hits_duplicates_and_capacity() -> None:
    class FixtureConnector(WttjPublicConnector):
        def search_page(self, query: str, page: int = 0, hits_per_page: int = 20, retries: int = 2):
            from scrappy.connectors.wttj import SearchPage

            if page > 0:
                offers = []
            else:
                offers = [
                    Offer(
                        source=self.name,
                        source_id=f"shared-{index}",
                        url=f"https://example.test/{query}/{index}",
                        title="Engineer",
                    )
                    for index in range(2)
                ]
            return SearchPage(offers=offers, query=query, page=page, hits=len(offers), nb_hits=2, nb_pages=1)

    result = FixtureConnector().discover_with_stats(["electronics", "signal"], max_pages=2, target_count=10)

    assert len(result.offers) == 2
    assert result.raw_hits == 4
    assert result.duplicate_hits == 2
    assert not result.target_reached
    assert result.pages[0].nb_hits == 2

from scrappy.connectors.indeed import IndeedApiConnector


def test_maps_indeed_api_payload_to_offers() -> None:
    class FixtureConnector(IndeedApiConnector):
        def _fetch_json(self, query: str, page: int, hits_per_page: int) -> dict:
            return {
                "total": 1,
                "jobs": [
                    {
                        "jobId": "abc123",
                        "jobTitle": "Electronics Engineer",
                        "companyName": "Deeptech",
                        "formattedLocation": "Paris",
                        "jobType": "Full-time",
                        "snippet": "Signal processing and instrumentation role.",
                        "url": "https://indeed.example/jobs/abc123",
                        "sponsored": True,
                    }
                ],
            }

    result = FixtureConnector(endpoint="https://indeed.example/api").discover_with_stats(
        ["electronics engineer"],
        max_pages=1,
        target_count=10,
    )

    assert result.provider == "indeed_api"
    assert result.raw_hits == 1
    assert result.pages[0].nb_hits == 1
    assert result.offers[0].source == "indeed_api"
    assert result.offers[0].source_id == "abc123"
    assert result.offers[0].company == "Deeptech"
    assert "sponsored" in result.offers[0].description


def test_requires_configured_endpoint_for_indeed_api() -> None:
    connector = IndeedApiConnector()

    try:
        connector.discover_with_stats(["electronics engineer"])
    except RuntimeError as error:
        assert "SCRAPPY_INDEED_API_URL" in str(error)
    else:
        raise AssertionError("Expected RuntimeError")


def test_requires_apify_token_for_apify_provider() -> None:
    connector = IndeedApiConnector(provider="apify")

    try:
        connector.discover_with_stats(["electronics engineer"])
    except RuntimeError as error:
        assert "SCRAPPY_INDEED_APIFY_TOKEN" in str(error)
    else:
        raise AssertionError("Expected RuntimeError")


def test_maps_apify_actor_payload_to_offer() -> None:
    class FixtureConnector(IndeedApiConnector):
        def _search_apify(self, query: str, max_items: int):
            from scrappy.connectors.base import SearchPage

            offer = self.offer_from_item(
                {
                    "positionName": "Electronics Engineer",
                    "salary": None,
                    "jobType": ["Fulltime"],
                    "company": "Deeptech",
                    "location": "Paris",
                    "url": "https://www.indeed.com/viewjob?jk=apify123",
                    "id": "apify123",
                    "description": "Signal processing instrumentation role.",
                    "isRemote": False,
                }
            )
            return SearchPage(offers=[offer], query=query, page=0, hits=1, nb_hits=1, nb_pages=1)

    result = FixtureConnector(provider="apify", apify_token="token").discover_with_stats(
        ["electronics engineer"],
        max_pages=2,
        target_count=10,
        hits_per_page=5,
    )

    assert result.offers[0].source_id == "apify123"
    assert result.offers[0].title == "Electronics Engineer"
    assert result.offers[0].company == "Deeptech"
    assert result.offers[0].contract_type == "Fulltime"


def test_builds_borderline_apify_input_shape() -> None:
    connector = IndeedApiConnector(
        provider="apify",
        apify_token="token",
        apify_actor_id="borderline~indeed-scraper",
        country="FR",
        location="Paris",
    )

    payload = connector._apify_input("electronics engineer", max_items=25)

    assert payload["query"] == "electronics engineer"
    assert payload["country"] == "fr"
    assert payload["maxRows"] == 25
    assert payload["jobType"] == "fulltime"

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

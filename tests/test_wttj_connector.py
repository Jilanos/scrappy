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

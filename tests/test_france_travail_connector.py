from scrappy.connectors.france_travail import FranceTravailConnector


def test_requires_france_travail_credentials() -> None:
    connector = FranceTravailConnector()

    try:
        connector.discover_with_stats(["electronics engineer"])
    except RuntimeError as error:
        assert "SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID" in str(error)
    else:
        raise AssertionError("Expected RuntimeError")


def test_maps_france_travail_offer_to_offer_model() -> None:
    connector = FranceTravailConnector(client_id="id", client_secret="secret")
    offer = connector.offer_from_item(
        {
            "id": "123ABC",
            "intitule": "Ingenieur electronique F/H",
            "description": "Traitement du signal et instrumentation. Teletravail partiel.",
            "entreprise": {"nom": "Deeptech"},
            "lieuTravail": {"libelle": "75 - PARIS 01"},
            "typeContrat": "CDI",
            "typeContratLibelle": "Contrat a duree indeterminee",
            "natureContrat": "Temps plein",
            "experienceLibelle": "3 ans",
            "salaire": {"libelle": "A negocier"},
            "origineOffre": {"urlOrigine": "https://candidat.francetravail.fr/offres/recherche/detail/123ABC"},
        }
    )

    assert offer.source == "france_travail"
    assert offer.source_id == "123ABC"
    assert offer.title == "Ingenieur electronique F/H"
    assert offer.company == "Deeptech"
    assert offer.location == "75 - PARIS 01"
    assert "CDI" in offer.contract_type
    assert offer.remote == "teletravail"


def test_discovers_france_travail_offers_with_pagination_stats() -> None:
    class FixtureConnector(FranceTravailConnector):
        def access_token(self) -> str:
            return "token"

        def _fetch_search(self, query: str, result_range: str):
            assert query == "electronique"
            assert result_range == "0-1"
            return (
                {
                    "resultats": [
                        {
                            "id": "1",
                            "intitule": "Ingenieur electronique",
                            "description": "Signal processing",
                            "entreprise": {"nom": "Deeptech"},
                            "lieuTravail": {"libelle": "75 - Paris"},
                            "typeContrat": "CDI",
                        },
                        {
                            "id": "2",
                            "intitule": "Ingenieur instrumentation",
                            "description": "Electronics",
                            "entreprise": {"nom": "Lab"},
                            "lieuTravail": {"libelle": "75 - Paris"},
                            "typeContrat": "CDI",
                        },
                    ]
                },
                "0-1/42",
            )

    result = FixtureConnector(client_id="id", client_secret="secret").discover_with_stats(
        ["electronics engineer"],
        max_pages=1,
        target_count=10,
        hits_per_page=2,
    )

    assert result.provider == "france_travail"
    assert result.raw_hits == 2
    assert result.pages[0].nb_hits == 42
    assert result.pages[0].nb_pages == 21
    assert result.offers[0].source_id == "1"


def test_translates_default_profile_query_for_france_travail() -> None:
    class FixtureConnector(FranceTravailConnector):
        def access_token(self) -> str:
            return "token"

        def _fetch_search(self, query: str, result_range: str):
            assert query == "electronique"
            return {"resultats": [], "total": 0}, "*/0"

    result = FixtureConnector(client_id="id", client_secret="secret").discover_with_stats(
        ["electronics engineer"],
        max_pages=1,
        target_count=10,
        hits_per_page=2,
    )

    assert result.raw_hits == 0
    assert result.pages[0].nb_hits == 0


def test_fetches_oauth_token_from_france_travail() -> None:
    class FixtureConnector(FranceTravailConnector):
        def _fetch_access_token(self) -> str:
            return "token"

    connector = FixtureConnector(client_id="id", client_secret="secret")

    assert connector.access_token() == "token"
    assert connector.access_token() == "token"

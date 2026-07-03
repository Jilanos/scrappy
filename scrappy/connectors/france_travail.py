from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scrappy.connectors.base import DiscoveryResult, SearchPage
from scrappy.models import Offer


DEFAULT_TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
DEFAULT_SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
FALLBACK_SEARCH_URL = "https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search"
DEFAULT_SCOPE = "api_offresdemploiv2 o2dsoffre"
DEFAULT_LOCATION = "75"
DEFAULT_REQUEST_INTERVAL_SECONDS = 0.4
MAX_RANGE_END = 1149


@dataclass
class FranceTravailConnector:
    client_id: str = ""
    client_secret: str = ""
    scope: str = DEFAULT_SCOPE
    search_url: str = DEFAULT_SEARCH_URL
    token_url: str = DEFAULT_TOKEN_URL
    location: str = DEFAULT_LOCATION
    contract_type: str = "CDI"
    timeout_seconds: int = 20
    user_agent: str = "scrappy-local-job-review/0.1"
    request_interval_seconds: float = DEFAULT_REQUEST_INTERVAL_SECONDS
    _access_token: str = field(default="", init=False, repr=False)
    _last_request_at: float = field(default=0.0, init=False, repr=False)

    @classmethod
    def from_env(cls) -> "FranceTravailConnector":
        return cls(
            client_id=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID", "").strip(),
            client_secret=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET", "").strip(),
            scope=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_SCOPE", DEFAULT_SCOPE).strip() or DEFAULT_SCOPE,
            search_url=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_SEARCH_URL", DEFAULT_SEARCH_URL).strip()
            or DEFAULT_SEARCH_URL,
            token_url=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_TOKEN_URL", DEFAULT_TOKEN_URL).strip()
            or DEFAULT_TOKEN_URL,
            location=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_LOCATION", DEFAULT_LOCATION).strip() or DEFAULT_LOCATION,
            contract_type=os.environ.get("SCRAPPY_FRANCE_TRAVAIL_CONTRACT", "CDI").strip(),
            request_interval_seconds=float(
                os.environ.get("SCRAPPY_FRANCE_TRAVAIL_REQUEST_INTERVAL_SECONDS", DEFAULT_REQUEST_INTERVAL_SECONDS)
            ),
        )

    @property
    def name(self) -> str:
        return "france_travail"

    def discover(
        self,
        queries: Iterable[str],
        max_pages: int = 5,
        target_count: int = 100,
        hits_per_page: int = 20,
    ) -> list[Offer]:
        return self.discover_with_stats(
            queries,
            max_pages=max_pages,
            target_count=target_count,
            hits_per_page=hits_per_page,
        ).offers

    def discover_with_stats(
        self,
        queries: Iterable[str],
        max_pages: int = 5,
        target_count: int = 100,
        hits_per_page: int = 20,
        time_budget_seconds: int = 0,
    ) -> DiscoveryResult:
        self._require_credentials()
        offers: dict[str, Offer] = {}
        pages: list[SearchPage] = []
        raw_hits = 0
        page_size = min(max(1, hits_per_page), 150)
        if time_budget_seconds > 0:
            return self._discover_until_deadline(
                queries,
                max_pages=max_pages,
                target_count=target_count,
                hits_per_page=page_size,
                time_budget_seconds=time_budget_seconds,
            )
        for page in range(max_pages):
            for query in queries:
                search_page = self.search_page(query=_france_travail_query(query), page=page, hits_per_page=page_size)
                pages.append(search_page)
                raw_hits += search_page.hits
                for offer in search_page.offers:
                    offers[offer.source_id] = offer
                if len(offers) >= target_count:
                    return self._result(offers, pages, raw_hits, True)
        return self._result(offers, pages, raw_hits, len(offers) >= target_count)

    def _discover_until_deadline(
        self,
        queries: Iterable[str],
        max_pages: int,
        target_count: int,
        hits_per_page: int,
        time_budget_seconds: int,
    ) -> DiscoveryResult:
        offers: dict[str, Offer] = {}
        pages: list[SearchPage] = []
        raw_hits = 0
        deadline = time.monotonic() + max(1, time_budget_seconds)
        translated_queries = _unique(_france_travail_query(query) for query in queries)
        if not translated_queries:
            translated_queries = [_france_travail_query("")]
        max_api_pages = (MAX_RANGE_END + hits_per_page) // hits_per_page
        page_limit = min(max_pages, max_api_pages)

        for page in range(page_limit):
            for query in translated_queries:
                if len(offers) >= target_count or time.monotonic() >= deadline:
                    return self._result(offers, pages, raw_hits, len(offers) >= target_count)
                try:
                    search_page = self.search_page(query=query, page=page, hits_per_page=hits_per_page)
                except RuntimeError:
                    continue
                pages.append(search_page)
                raw_hits += search_page.hits
                for offer in search_page.offers:
                    offers[offer.source_id] = offer

        return self._result(offers, pages, raw_hits, len(offers) >= target_count)

    def search_page(self, query: str, page: int = 0, hits_per_page: int = 20) -> SearchPage:
        start = page * hits_per_page
        end = start + hits_per_page - 1
        payload, content_range = self._fetch_search(query=query, result_range=f"{start}-{end}")
        items = payload.get("resultats") or []
        if not isinstance(items, list):
            items = []
        offers = [self.offer_from_item(item) for item in items if isinstance(item, dict)]
        total = _total_from_content_range(content_range) or int(payload.get("total") or len(offers))
        return SearchPage(
            offers=offers,
            query=query,
            page=page,
            hits=len(offers),
            nb_hits=total,
            nb_pages=_nb_pages(total, hits_per_page),
        )

    def offer_from_item(self, item: dict) -> Offer:
        source_id = str(item.get("id") or item.get("reference") or "")
        title = str(item.get("intitule") or item.get("titre") or "")
        company = _company_name(item)
        location = _location_text(item)
        contract_type = " ".join(
            part
            for part in [
                str(item.get("typeContrat") or ""),
                str(item.get("typeContratLibelle") or ""),
                str(item.get("natureContrat") or ""),
            ]
            if part
        )
        description = "\n\n".join(
            part
            for part in [
                title,
                company,
                str(item.get("description") or ""),
                _salary_text(item),
                _remote_text(item),
            ]
            if part
        )
        url = _offer_url(item, source_id)
        if not source_id:
            source_id = hashlib.sha256((url + title + company).encode("utf-8")).hexdigest()[:20]
        content_hash = hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        return Offer(
            source=self.name,
            source_id=source_id,
            url=url,
            title=title,
            company=company,
            location=location,
            remote=_remote_text(item),
            seniority=str(item.get("experienceLibelle") or ""),
            contract_type=contract_type,
            description=description,
            content_hash=content_hash,
        )

    def _fetch_search(self, query: str, result_range: str, retries: int = 2) -> tuple[dict, str]:
        params = {
            "motsCles": query,
            "range": result_range,
        }
        if self.location:
            if self.location.isdigit() and len(self.location) <= 3:
                params["departement"] = self.location
            else:
                params["commune"] = self.location
        if self.contract_type:
            params["typeContrat"] = self.contract_type
        request = Request(
            f"{self.search_url}?{urlencode(params)}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token()}",
                "User-Agent": self.user_agent,
            },
        )
        for attempt in range(retries + 1):
            self._throttle()
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    if response.status == 204 or not body.strip():
                        return {"resultats": [], "total": 0}, response.headers.get("Content-Range", "")
                    return json.loads(body), response.headers.get("Content-Range", "")
            except HTTPError as error:
                if error.code == 204:
                    return {"resultats": [], "total": 0}, ""
                if (error.code == 429 or 500 <= error.code <= 599) and attempt < retries:
                    retry_after = _retry_after_seconds(error.headers.get("Retry-After", ""))
                    time.sleep(retry_after or max(self.request_interval_seconds * 2, 1.0))
                    continue
                raise RuntimeError(f"France Travail search failed for query={query!r}: HTTP {error.code}") from error
            except (URLError, TimeoutError, json.JSONDecodeError) as error:
                if attempt < retries:
                    time.sleep(max(self.request_interval_seconds, 0.2))
                    continue
                raise RuntimeError(f"France Travail search failed for query={query!r}") from error
        raise RuntimeError(f"France Travail search failed for query={query!r}")

    def access_token(self) -> str:
        if not self._access_token:
            self._access_token = self._fetch_access_token()
        return self._access_token

    def _fetch_access_token(self) -> str:
        self._require_credentials()
        body = urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope,
            }
        ).encode("utf-8")
        request = Request(
            self.token_url,
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": self.user_agent,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise RuntimeError(f"France Travail OAuth failed: HTTP {error.code}") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError("France Travail OAuth failed") from error
        token = str(payload.get("access_token") or "")
        if not token:
            raise RuntimeError("France Travail OAuth response did not contain access_token")
        return token

    def _require_credentials(self) -> None:
        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "France Travail connector requires SCRAPPY_FRANCE_TRAVAIL_CLIENT_ID and "
                "SCRAPPY_FRANCE_TRAVAIL_CLIENT_SECRET"
            )

    def _throttle(self) -> None:
        if self.request_interval_seconds <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait = self.request_interval_seconds - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()

    def _result(
        self,
        offers: dict[str, Offer],
        pages: list[SearchPage],
        raw_hits: int,
        target_reached: bool,
    ) -> DiscoveryResult:
        return DiscoveryResult(
            provider=self.name,
            offers=list(offers.values()),
            pages=pages,
            raw_hits=raw_hits,
            duplicate_hits=raw_hits - len(offers),
            target_reached=target_reached,
        )


def _company_name(item: dict) -> str:
    company = item.get("entreprise")
    if isinstance(company, dict):
        return str(company.get("nom") or company.get("libelle") or "")
    return str(company or "")


def _location_text(item: dict) -> str:
    location = item.get("lieuTravail")
    if isinstance(location, dict):
        return str(location.get("libelle") or location.get("commune") or location.get("codePostal") or "")
    return str(location or "")


def _salary_text(item: dict) -> str:
    salary = item.get("salaire")
    if isinstance(salary, dict):
        return str(salary.get("libelle") or "")
    return str(salary or "")


def _remote_text(item: dict) -> str:
    fields = [
        item.get("teletravail"),
        item.get("teletravailLibelle"),
        item.get("remote"),
        item.get("description"),
    ]
    text = " ".join(str(field) for field in fields if field)
    return "teletravail" if re.search(r"\b(?:teletravail|remote|distance)\b", text, re.IGNORECASE) else ""


def _offer_url(item: dict, source_id: str) -> str:
    origin = item.get("origineOffre")
    if isinstance(origin, dict) and origin.get("urlOrigine"):
        return str(origin["urlOrigine"])
    return f"https://candidat.francetravail.fr/offres/recherche/detail/{source_id}"


def _total_from_content_range(value: str) -> int:
    match = re.search(r"/(\d+)$", value or "")
    return int(match.group(1)) if match else 0


def _nb_pages(total: int, hits_per_page: int) -> int:
    if hits_per_page <= 0:
        return 0
    return (total + hits_per_page - 1) // hits_per_page


def _retry_after_seconds(value: str) -> float:
    try:
        return max(0.0, float(value))
    except ValueError:
        return 0.0


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _france_travail_query(query: str) -> str:
    translations = {
        "electronics engineer": "electronique",
        "signal processing engineer": "traitement signal",
        "r&d engineer": "ingenieur recherche developpement",
        "medical imaging engineer": "imagerie medicale",
        "deep tech engineer": "ingenieur deep tech",
        "electrical integration engineer": "integration electrique",
        "system integration engineer": "integration systeme",
        "ultrasound engineer": "ultrasons",
        "biomedical engineer": "biomedical",
        "fpga engineer": "FPGA",
        "python scientific tooling engineer": "python scientifique",
        "hardware validation engineer": "validation materiel",
        "prototype validation engineer": "validation prototype",
        "technical project engineer": "chef projet technique",
        "signal processing": "traitement signal",
        "electronics": "electronique",
        "instrumentation": "instrumentation",
        "electrical architecture": "architecture electrique",
        "medical imaging": "imagerie medicale",
        "ultrasound": "ultrasons",
        "system integration": "integration systeme",
        "hardware debugging": "debug materiel",
        "data science": "data science",
        "project management": "gestion projet",
        "supplier coordination": "coordination fournisseur",
        "prototype validation": "validation prototype",
    }
    return translations.get(query.strip().lower(), query)

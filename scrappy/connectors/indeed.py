from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from scrappy.connectors.base import DiscoveryResult, SearchPage
from scrappy.models import Offer


DEFAULT_INDEED_LOCATION = "Paris"
DEFAULT_INDEED_COUNTRY = "FR"
DEFAULT_APIFY_ACTOR_ID = "misceres~indeed-scraper"


@dataclass(frozen=True)
class IndeedApiConnector:
    endpoint: str = ""
    api_key: str = ""
    provider: str = "generic"
    apify_token: str = ""
    apify_actor_id: str = DEFAULT_APIFY_ACTOR_ID
    country: str = DEFAULT_INDEED_COUNTRY
    location: str = DEFAULT_INDEED_LOCATION
    timeout_seconds: int = 20
    user_agent: str = "scrappy-local-job-review/0.1"

    @classmethod
    def from_env(cls) -> "IndeedApiConnector":
        return cls(
            endpoint=os.environ.get("SCRAPPY_INDEED_API_URL", "").strip(),
            api_key=os.environ.get("SCRAPPY_INDEED_API_KEY", "").strip(),
            provider=os.environ.get("SCRAPPY_INDEED_PROVIDER", "generic").strip().lower() or "generic",
            apify_token=os.environ.get("SCRAPPY_INDEED_APIFY_TOKEN", "").strip(),
            apify_actor_id=os.environ.get("SCRAPPY_INDEED_APIFY_ACTOR", DEFAULT_APIFY_ACTOR_ID).strip()
            or DEFAULT_APIFY_ACTOR_ID,
            country=os.environ.get("SCRAPPY_INDEED_COUNTRY", DEFAULT_INDEED_COUNTRY).strip() or DEFAULT_INDEED_COUNTRY,
            location=os.environ.get("SCRAPPY_INDEED_LOCATION", DEFAULT_INDEED_LOCATION).strip() or DEFAULT_INDEED_LOCATION,
        )

    @property
    def name(self) -> str:
        return "indeed_api"

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
    ) -> DiscoveryResult:
        if self.provider == "apify":
            return self._discover_apify(
                queries,
                max_pages=max_pages,
                target_count=target_count,
                hits_per_page=hits_per_page,
            )
        if not self.endpoint:
            raise RuntimeError("Indeed API connector requires SCRAPPY_INDEED_API_URL or SCRAPPY_INDEED_PROVIDER=apify")

        offers: dict[str, Offer] = {}
        pages: list[SearchPage] = []
        raw_hits = 0
        for page in range(max_pages):
            for query in queries:
                search_page = self.search_page(query, page=page, hits_per_page=hits_per_page)
                pages.append(search_page)
                raw_hits += search_page.hits
                for offer in search_page.offers:
                    offers[offer.source_id] = offer
                if len(offers) >= target_count:
                    return self._result(offers, pages, raw_hits, True)
        return self._result(offers, pages, raw_hits, len(offers) >= target_count)

    def search_page(self, query: str, page: int = 0, hits_per_page: int = 20) -> SearchPage:
        payload = self._fetch_json(query=query, page=page, hits_per_page=hits_per_page)
        jobs = _job_items(payload)
        offers = [self.offer_from_item(item) for item in jobs]
        total = _total_hits(payload, default=len(jobs))
        return SearchPage(
            offers=offers,
            query=query,
            page=page,
            hits=len(offers),
            nb_hits=total,
            nb_pages=_nb_pages(total, hits_per_page),
        )

    def offer_from_item(self, item: dict) -> Offer:
        title = _pick(item, "title", "jobTitle", "job_title", "positionName", "name")
        company = _pick(item, "company", "companyName", "company_name", "employer")
        location = _pick(item, "location", "formattedLocation", "jobLocation", "city")
        remote = _pick(item, "remote", "isRemote", "workplaceType", "workplace_type")
        contract_type = _pick(item, "contract_type", "jobType", "employmentType", "employment_type")
        description = "\n\n".join(
            part
            for part in [
                title,
                company,
                _pick(item, "snippet", "summary", "description", "jobDescription"),
                _pick(item, "salary", "salarySnippet"),
                _flags_text(item),
            ]
            if part
        )
        url = _pick(item, "url", "jobUrl", "job_url", "link", "applyUrl")
        source_id = _pick(item, "id", "jobId", "job_id", "key", "jobkey", "jobKey", "indeedApplyJobId")
        if not source_id:
            source_id = hashlib.sha256((url or json.dumps(item, sort_keys=True)).encode("utf-8")).hexdigest()[:20]
        content_hash = hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        return Offer(
            source=self.name,
            source_id=source_id,
            url=url or f"https://www.indeed.com/viewjob?jk={source_id}",
            title=title,
            company=company,
            location=location,
            remote=remote,
            seniority=_pick(item, "seniority", "experienceLevel"),
            contract_type=contract_type,
            description=description,
            content_hash=content_hash,
        )

    def _fetch_json(self, query: str, page: int, hits_per_page: int) -> dict:
        params = urlencode(
            {
                "q": query,
                "query": query,
                "l": self.location,
                "location": self.location,
                "start": page * hits_per_page,
                "page": page + 1,
                "limit": hits_per_page,
            }
        )
        separator = "&" if "?" in self.endpoint else "?"
        request = Request(
            f"{self.endpoint}{separator}{params}",
            headers=self._headers(),
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Indeed API request failed for query={query!r} page={page + 1}") from error

    def _discover_apify(
        self,
        queries: Iterable[str],
        max_pages: int,
        target_count: int,
        hits_per_page: int,
    ) -> DiscoveryResult:
        if not self.apify_token:
            raise RuntimeError("Apify Indeed connector requires SCRAPPY_INDEED_APIFY_TOKEN")

        offers: dict[str, Offer] = {}
        pages: list[SearchPage] = []
        raw_hits = 0
        per_query_limit = max(1, min(target_count, max_pages * hits_per_page))
        for query in queries:
            search_page = self._search_apify(query, max_items=per_query_limit)
            pages.append(search_page)
            raw_hits += search_page.hits
            for offer in search_page.offers:
                offers[offer.source_id] = offer
            if len(offers) >= target_count:
                return self._result(offers, pages, raw_hits, True)
        return self._result(offers, pages, raw_hits, len(offers) >= target_count)

    def _search_apify(self, query: str, max_items: int) -> SearchPage:
        payload = self._apify_input(query=query, max_items=max_items)
        actor_id = quote(self.apify_actor_id, safe="~")
        params = urlencode({"token": self.apify_token, "format": "json", "clean": "true", "timeout": self.timeout_seconds})
        request = Request(
            f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?{params}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": self.user_agent},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds + 5) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code == 408:
                raise RuntimeError(
                    "Apify actor timed out before returning dataset items; lower --target-offers/--max-pages or run the actor asynchronously"
                ) from error
            raise RuntimeError(f"Apify Indeed request failed for query={query!r}: HTTP {error.code}") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Apify Indeed request failed for query={query!r}") from error

        items = data if isinstance(data, list) else _job_items(data)
        offers = [self.offer_from_item(item) for item in items if isinstance(item, dict)]
        return SearchPage(
            offers=offers,
            query=query,
            page=0,
            hits=len(offers),
            nb_hits=len(offers),
            nb_pages=1,
        )

    def _apify_input(self, query: str, max_items: int) -> dict:
        if self.apify_actor_id == "borderline~indeed-scraper":
            return {
                "country": self.country.lower(),
                "query": query,
                "location": self.location,
                "maxRows": max_items,
                "jobType": "fulltime",
                "sort": "relevance",
                "enableUniqueJobs": True,
            }
        return {
            "country": self.country.upper(),
            "location": self.location,
            "maxConcurrency": 5,
            "maxItems": max_items,
            "position": query,
            "saveOnlyUniqueItems": True,
        }

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

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


def _job_items(payload: dict) -> list[dict]:
    for key in ("jobs", "results", "data", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [_unwrap_item(item) for item in value if isinstance(item, dict)]
    nested = payload.get("data")
    if isinstance(nested, dict):
        return _job_items(nested)
    return []


def _total_hits(payload: dict, default: int) -> int:
    for key in ("total", "totalResults", "total_results", "count", "nbHits"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return default


def _nb_pages(total: int, hits_per_page: int) -> int:
    if hits_per_page <= 0:
        return 0
    return (total + hits_per_page - 1) // hits_per_page


def _pick(item: dict, *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        if isinstance(value, dict):
            value = value.get("text") or value.get("label") or value.get("name")
        if isinstance(value, list):
            value = ", ".join(str(part) for part in value)
        if isinstance(value, bool):
            value = "remote" if value else ""
        text = str(value).strip()
        if text:
            return text
    return ""


def _unwrap_item(item: dict) -> dict:
    nested = item.get("data")
    return nested if isinstance(nested, dict) else item


def _flags_text(item: dict) -> str:
    flags = []
    for key in ("sponsored", "isSponsored", "promoted", "isPromoted", "repost", "isRepost"):
        if item.get(key):
            flags.append(key)
    return " ".join(flags)

from __future__ import annotations

import hashlib
import html
import json
import re
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode, urljoin
from urllib.request import Request, urlopen

from scrappy.models import Offer


WTTJ_BASE = "https://www.welcometothejungle.com"
ALGOLIA_APP_ID = "CSEKHVMS53"
ALGOLIA_SEARCH_KEY = "4bd8f6215d0cc52b26430765769e65a0"
ALGOLIA_ENDPOINT = "https://csekhvms53-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_JOBS_INDEX = "wk_cms_jobs_production"


@dataclass(frozen=True)
class SearchPage:
    offers: list[Offer]
    query: str
    page: int
    hits: int
    nb_hits: int
    nb_pages: int


@dataclass(frozen=True)
class DiscoveryResult:
    offers: list[Offer]
    pages: list[SearchPage]
    raw_hits: int
    duplicate_hits: int
    target_reached: bool


@dataclass(frozen=True)
class WttjPublicConnector:
    locale: str = "en"
    timeout_seconds: int = 20
    user_agent: str = "scrappy-local-job-review/0.1"

    @property
    def name(self) -> str:
        return "wttj_algolia"

    def discover(
        self,
        queries: Iterable[str],
        max_pages: int = 15,
        target_count: int = 300,
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
        max_pages: int = 15,
        target_count: int = 300,
        hits_per_page: int = 20,
    ) -> DiscoveryResult:
        offers: dict[str, Offer] = {}
        pages: list[SearchPage] = []
        raw_hits = 0
        query_list = list(queries)
        for page in range(1, max_pages + 1):
            for query in query_list:
                search_page = self.search_page(query, page=page - 1, hits_per_page=hits_per_page)
                pages.append(search_page)
                raw_hits += search_page.hits
                for offer in search_page.offers:
                    offers[offer.source_id] = offer
                if len(offers) >= target_count:
                    return DiscoveryResult(
                        offers=list(offers.values()),
                        pages=pages,
                        raw_hits=raw_hits,
                        duplicate_hits=raw_hits - len(offers),
                        target_reached=True,
                    )
        return DiscoveryResult(
            offers=list(offers.values()),
            pages=pages,
            raw_hits=raw_hits,
            duplicate_hits=raw_hits - len(offers),
            target_reached=len(offers) >= target_count,
        )

    def search(
        self,
        query: str,
        page: int = 0,
        hits_per_page: int = 20,
        retries: int = 2,
    ) -> list[Offer]:
        return self.search_page(query, page=page, hits_per_page=hits_per_page, retries=retries).offers

    def search_page(
        self,
        query: str,
        page: int = 0,
        hits_per_page: int = 20,
        retries: int = 2,
    ) -> SearchPage:
        params = urlencode({"query": query, "hitsPerPage": hits_per_page, "page": page})
        payload = json.dumps(
            {"requests": [{"indexName": ALGOLIA_JOBS_INDEX, "params": params}]}
        ).encode("utf-8")
        request = Request(
            ALGOLIA_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Origin": WTTJ_BASE,
                "Referer": self.search_url(query, page + 1),
                "User-Agent": self.user_agent,
                "X-Algolia-API-Key": ALGOLIA_SEARCH_KEY,
                "X-Algolia-Application-Id": ALGOLIA_APP_ID,
            },
        )
        data = self._post_json(request, retries=retries)
        result = data.get("results", [{}])[0]
        hits = result.get("hits", [])
        return SearchPage(
            offers=[self.offer_from_hit(hit) for hit in hits],
            query=query,
            page=page,
            hits=len(hits),
            nb_hits=int(result.get("nbHits") or 0),
            nb_pages=int(result.get("nbPages") or 0),
        )

    def search_url(self, query: str, page: int = 1) -> str:
        return (
            f"{WTTJ_BASE}/{self.locale}/jobs"
            f"?query={quote_plus(query)}&aroundQuery={quote_plus('Paris, France')}&page={page}"
        )

    def offer_from_hit(self, hit: dict) -> Offer:
        org = hit.get("organization") or {}
        office = hit.get("office") or {}
        offices = hit.get("offices") or []
        first_office = office or (offices[0] if offices else {})
        org_slug = org.get("slug") or (hit.get("website") or {}).get("reference") or "unknown"
        job_slug = hit.get("slug") or hit.get("reference") or str(hit.get("objectID") or "")
        url = f"{WTTJ_BASE}/{self.locale}/companies/{org_slug}/jobs/{job_slug}"
        title = str(hit.get("name") or "")
        company = str(org.get("name") or "")
        location = _office_location(first_office)
        remote = str(hit.get("remote") or "")
        seniority = _seniority_from_experience(hit)
        contract_type = _localized(hit.get("contract_type_names")) or str(hit.get("contract_type") or "")
        description = "\n\n".join(
            part
            for part in [
                title,
                company,
                str(hit.get("profile") or ""),
                str(hit.get("description") or ""),
                _sectors(hit),
            ]
            if part
        )
        source_id = str(hit.get("objectID") or hit.get("reference") or f"{org_slug}:{job_slug}")
        content_hash = hashlib.sha256(
            json.dumps(hit, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return Offer(
            source=self.name,
            source_id=source_id,
            url=url,
            title=title,
            company=company,
            location=location,
            remote=remote,
            seniority=seniority,
            contract_type=contract_type,
            description=description,
            content_hash=content_hash,
        )

    def parse_search_html(self, body: str, source_url: str) -> list[Offer]:
        links = sorted(set(_job_links(body)))
        offers: list[Offer] = []
        for link in links:
            absolute = urljoin(WTTJ_BASE, link)
            slug = _source_id_from_url(absolute)
            context = _nearby_text(body, link)
            title, company = _guess_title_company(context)
            offers.append(
                Offer(
                    source=self.name,
                    source_id=slug,
                    url=absolute,
                    title=title or slug.replace("-", " "),
                    company=company,
                    location="",
                    remote="",
                    description=context or f"Discovered from {source_url}",
                    content_hash=hashlib.sha256((absolute + context).encode("utf-8")).hexdigest(),
                )
            )
        return offers

    def _fetch(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")

    def _post_json(self, request: Request, retries: int) -> dict:
        last_error: HTTPError | URLError | TimeoutError | None = None
        for attempt in range(retries + 1):
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError) as error:
                last_error = error
                if attempt >= retries:
                    break
                time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"WTTJ Algolia request failed after {retries + 1} attempts") from last_error


def _job_links(body: str) -> Iterable[str]:
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', body)
    for href in hrefs:
        decoded = html.unescape(href)
        if re.search(r"/(?:en|fr|en-GB)/companies/[^/]+/jobs/[^/?#]+", decoded):
            yield decoded


def _source_id_from_url(url: str) -> str:
    match = re.search(r"/companies/([^/]+)/jobs/([^/?#]+)", url)
    if not match:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return f"{match.group(1)}:{match.group(2)}"


def _nearby_text(body: str, needle: str, radius: int = 900) -> str:
    index = body.find(needle)
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(body), index + radius)
    snippet = re.sub(r"<script.*?</script>", " ", body[start:end], flags=re.DOTALL)
    snippet = re.sub(r"<[^>]+>", " ", snippet)
    snippet = html.unescape(snippet)
    return re.sub(r"\s+", " ", snippet).strip()


def _guess_title_company(context: str) -> tuple[str, str]:
    if not context:
        return "", ""
    parts = [part.strip(" -|") for part in re.split(r"\s{2,}|\|", context) if part.strip()]
    title = parts[0] if parts else ""
    company = parts[1] if len(parts) > 1 else ""
    return title[:160], company[:120]


def _office_location(office: dict) -> str:
    parts = [
        office.get("city"),
        office.get("district"),
        office.get("state"),
        office.get("country"),
    ]
    return ", ".join(str(part) for part in parts if part)


def _seniority_from_experience(hit: dict) -> str:
    minimum = hit.get("experience_level_minimum")
    if isinstance(minimum, int):
        if minimum >= 5:
            return "senior"
        if minimum >= 2:
            return "confirmed"
        return "junior"
    return ""


def _localized(value: object, locale: str = "en") -> str:
    if isinstance(value, dict):
        return str(value.get(locale) or value.get("fr") or next(iter(value.values()), ""))
    return ""


def _sectors(hit: dict) -> str:
    names = hit.get("sectors_name")
    if not isinstance(names, dict):
        return ""
    values = names.get("en") or names.get("fr") or []
    output: list[str] = []
    for item in values:
        if isinstance(item, dict):
            output.extend(str(value) for value in item.values())
    return ", ".join(output)

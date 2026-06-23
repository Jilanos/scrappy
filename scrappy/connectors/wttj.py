from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen

from scrappy.models import Offer


WTTJ_BASE = "https://www.welcometothejungle.com"


@dataclass(frozen=True)
class WttjPublicConnector:
    locale: str = "en"
    timeout_seconds: int = 20
    user_agent: str = "scrappy-local-job-review/0.1"

    @property
    def name(self) -> str:
        return "wttj_public"

    def discover(self, queries: Iterable[str], max_pages: int = 1) -> list[Offer]:
        offers: dict[str, Offer] = {}
        for query in queries:
            for page in range(1, max_pages + 1):
                url = self.search_url(query, page)
                body = self._fetch(url)
                for offer in self.parse_search_html(body, source_url=url):
                    offers[offer.source_id] = offer
        return list(offers.values())

    def search_url(self, query: str, page: int = 1) -> str:
        return (
            f"{WTTJ_BASE}/{self.locale}/jobs"
            f"?query={quote_plus(query)}&aroundQuery={quote_plus('Paris, France')}&page={page}"
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

import json
import re
from datetime import date
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import httpx

from app.collectors.base import BaseCollector
from app.schemas.race import RaceDetail


class MarathonGoCollector(BaseCollector):
    source_name = "marathongo"
    base_url = "https://marathongo.co.kr"
    home_url = "https://marathongo.co.kr/"
    listing_statuses = ("접수중", "오픈예정")
    max_listing_pages = 12

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(
            follow_redirects=True,
            timeout=httpx.Timeout(20.0),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/136.0.0.0 Safari/537.36"
                )
            },
        )

    def collect(self, limit: int | None = None) -> list[RaceDetail]:
        detail_urls = self._collect_detail_urls(limit=limit)

        races: list[RaceDetail] = []
        for detail_url in detail_urls:
            try:
                detail_html = self._fetch_text(detail_url)
                races.append(self._parse_detail_page(detail_url, detail_html))
            except Exception:
                continue
        return races

    def _collect_detail_urls(self, limit: int | None = None) -> list[str]:
        seen: set[str] = set()
        detail_urls: list[str] = []

        for listing_url in self._listing_urls():
            urls = self._collect_listing_detail_urls(listing_url, limit=limit, seen=seen)
            detail_urls.extend(urls)
            if limit is not None and len(detail_urls) >= limit:
                return detail_urls[:limit]

        return detail_urls

    def _listing_urls(self) -> list[str]:
        urls = [self.home_url]
        for status in self.listing_statuses:
            urls.append(f"{self.home_url}?status={status}")
        return urls

    def _collect_listing_detail_urls(
        self,
        start_url: str,
        limit: int | None,
        seen: set[str],
    ) -> list[str]:
        listing_queue = [start_url]
        visited_listing_urls: set[str] = set()
        collected: list[str] = []
        page_count = 0

        while listing_queue and page_count < self.max_listing_pages:
            listing_url = listing_queue.pop(0)
            if listing_url in visited_listing_urls:
                continue

            visited_listing_urls.add(listing_url)
            page_count += 1

            try:
                html = self._fetch_text(listing_url)
            except Exception:
                continue

            page_urls = self._extract_detail_urls(html)
            for detail_url in page_urls:
                if detail_url in seen:
                    continue
                seen.add(detail_url)
                collected.append(detail_url)
                if limit is not None and len(seen) >= limit:
                    return collected

            next_urls = self._extract_listing_pagination_urls(html, current_url=listing_url)
            if next_urls:
                for next_url in next_urls:
                    if next_url not in visited_listing_urls and next_url not in listing_queue:
                        listing_queue.append(next_url)
                continue

            next_page_url = self._with_page(listing_url, self._current_page(listing_url) + 1)
            if next_page_url not in visited_listing_urls and next_page_url not in listing_queue:
                listing_queue.append(next_page_url)

        return collected

    def _fetch_text(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()
        return response.text

    def _extract_detail_urls(self, html: str) -> list[str]:
        matches = re.findall(r'href="(/raceDetail/[^"]+)"', html)
        seen: set[str] = set()
        urls: list[str] = []
        for match in matches:
            full_url = urljoin(self.base_url, match)
            if full_url in seen:
                continue
            seen.add(full_url)
            urls.append(full_url)
        return urls

    def _extract_listing_pagination_urls(self, html: str, current_url: str) -> list[str]:
        matches = re.findall(r'href="([^"]+page=\d+[^"]*)"', html)
        urls: list[str] = []
        seen: set[str] = set()
        current_path = urlparse(current_url).path
        for match in matches:
            full_url = urljoin(self.base_url, match.replace("&amp;", "&"))
            parsed = urlparse(full_url)
            if parsed.netloc and "marathongo.co.kr" not in parsed.netloc:
                continue
            if "/raceDetail/" in parsed.path:
                continue
            if parsed.path not in {"", "/", current_path}:
                continue
            if full_url in seen:
                continue
            seen.add(full_url)
            urls.append(full_url)
        return urls

    def _parse_detail_page(self, source_url: str, html: str) -> RaceDetail:
        next_data = self._extract_next_data(html)
        raw = next_data["props"]["pageProps"]["raceDetail"]
        today = date.today()
        event_date = date.fromisoformat(raw["raceDate"])
        registration_open_at = self._parse_date(raw.get("applicationStartDate"))
        registration_close_at = self._parse_date(raw.get("applicationEndDate"))
        official_url = self._normalize_url(raw.get("homepageUrl"))
        apply_url = self._extract_apply_url(html) or official_url
        thumbnail_url = self._extract_thumbnail_url(html)
        course_note = self._infer_course_note(raw.get("raceName"), raw.get("place"))

        return RaceDetail(
            slug=raw["raceDetailUrl"],
            title=raw["raceName"],
            region=raw.get("region") or raw.get("regionCategory") or self._infer_region_from_url(source_url),
            venue=raw.get("place") or "장소 미정",
            event_date=event_date,
            registration_status=self._derive_registration_status(
                today=today,
                registration_open_at=registration_open_at,
                registration_close_at=registration_close_at,
                is_sold_out=raw.get("isSoldOut"),
                is_paused=raw.get("isPaused"),
            ),
            distances=self._parse_distances(raw.get("raceTypeList")),
            thumbnail_url=thumbnail_url,
            is_bookmarked=False,
            start_time=raw.get("raceStart"),
            registration_open_at=registration_open_at,
            registration_close_at=registration_close_at,
            event_status="upcoming" if event_date >= today else "finished",
            official_url=official_url,
            apply_url=apply_url,
            contact_email=raw.get("email"),
            contact_phone=raw.get("phone"),
            organizer=raw.get("host"),
            entry_fee_note=self._extract_entry_fee_note(html),
            cutoff_note=self._extract_cutoff_note(html),
            course_note=course_note,
            description=(raw.get("intro") or "").strip(),
            source_url=source_url,
            last_checked_at=today,
        )

    def _extract_next_data(self, html: str) -> dict:
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json" crossorigin="">(.*?)</script>',
            html,
            flags=re.DOTALL,
        )
        if match is None:
            raise ValueError("Unable to locate __NEXT_DATA__ payload")
        return json.loads(match.group(1))

    def _extract_apply_url(self, html: str) -> str | None:
        match = re.search(r'href="(https?://[^"]+marathongo[^"]+utm_source[^"]+|https?://[^"]+)"[^>]*>\s*<button[^>]*>신청하기</button>', html)
        if match is None:
            return None
        return self._normalize_url(match.group(1).replace("&amp;", "&"))

    def _extract_thumbnail_url(self, html: str) -> str | None:
        match = re.search(r'src="(https://marathongo\.co\.kr/assets/image/race/[^"]+)"', html)
        if match is None:
            return None
        return match.group(1)

    def _extract_entry_fee_note(self, html: str) -> str | None:
        match = re.search(r"([1-9]\d{0,2}(?:,\d{3})*\s*원)", html)
        if match is None:
            return None
        return match.group(1).replace(" ", "")

    def _extract_cutoff_note(self, html: str) -> str | None:
        match = re.search(r"(\d+\s*시간|\d+\s*분)\s*(?:컷오프|제한시간)", html)
        if match:
            return re.sub(r"\s+", "", match.group(0))
        return None

    def _infer_course_note(self, race_name: str | None, place: str | None) -> str | None:
        text = " ".join(filter(None, [race_name, place])).casefold()
        if any(keyword in text for keyword in ["trail", "트레일", "산", "오름"]):
            return "오르내림이 있는 트레일 코스 추정"
        if any(keyword in text for keyword in ["해변", "바다", "coast", "ocean", "한강"]):
            return "바람 영향을 받을 수 있는 개방형 코스 추정"
        if any(keyword in text for keyword in ["공원", "park", "도심", "city"]):
            return "로드 중심의 비교적 평탄한 코스 추정"
        return None

    def _parse_distances(self, value: str | None) -> list[str]:
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    def _parse_date(self, value: str | None) -> date | None:
        if not value:
            return None
        return date.fromisoformat(value)

    def _normalize_url(self, value: str | None) -> str | None:
        if not value:
            return None
        return value.strip()

    def _infer_region_from_url(self, url: str) -> str:
        if "/overseas/" in url:
            return "해외"
        return "국내"

    def _derive_registration_status(
        self,
        *,
        today: date,
        registration_open_at: date | None,
        registration_close_at: date | None,
        is_sold_out: bool | None,
        is_paused: bool | None,
    ) -> str:
        if is_sold_out or is_paused:
            return "registration_closed"
        if registration_open_at and today < registration_open_at:
            return "registration_upcoming"
        if registration_close_at and today > registration_close_at:
            return "registration_closed"
        return "registration_open"

    def _current_page(self, url: str) -> int:
        parsed = urlparse(url)
        page_value = parse_qs(parsed.query).get("page", ["1"])[0]
        try:
            return int(page_value)
        except ValueError:
            return 1

    def _with_page(self, url: str, page: int) -> str:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        query["page"] = [str(page)]
        encoded = urlencode(query, doseq=True)
        return urlunparse(parsed._replace(query=encoded))

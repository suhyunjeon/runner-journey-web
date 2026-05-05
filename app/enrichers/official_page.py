import html
import re

import httpx

from app.schemas.race import RaceDetail


class OfficialPageEnricher:
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

    def enrich(self, race: RaceDetail) -> RaceDetail:
        target_url = str(race.apply_url or race.official_url or "")
        if not target_url:
            return race

        try:
            response = self.client.get(target_url)
            response.raise_for_status()
        except Exception:
            return race

        text = self._to_text(response.text)
        entry_fee = race.entry_fee_note or self._extract_entry_fee(text)
        cutoff = race.cutoff_note or self._extract_cutoff(text)
        gift = self._extract_gift(text)
        course_note = race.course_note or self._extract_course_note(text)

        if gift and gift not in race.description:
            race.description = f"{race.description}\n\n기념품: {gift}".strip()

        race.entry_fee_note = entry_fee
        race.cutoff_note = cutoff
        race.course_note = course_note
        return race

    def _to_text(self, html_text: str) -> str:
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html_text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_entry_fee(self, text: str) -> str | None:
        patterns = [
            r"(?:참가비|접수비|참가금)\s*[:：]?\s*([0-9]{1,3}(?:,[0-9]{3})*\s*원)",
            r"([0-9]{1,3}(?:,[0-9]{3})*\s*원)\s*(?:참가비|접수비|참가금)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return re.sub(r"\s+", "", match.group(1))
        return None

    def _extract_cutoff(self, text: str) -> str | None:
        patterns = [
            r"(?:제한시간|컷오프)\s*[:：]?\s*([0-9]+\s*시간(?:\s*[0-9]+\s*분)?|[0-9]+\s*분)",
            r"([0-9]+\s*시간(?:\s*[0-9]+\s*분)?|[0-9]+\s*분)\s*(?:제한시간|컷오프)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return re.sub(r"\s+", "", match.group(1))
        return None

    def _extract_gift(self, text: str) -> str | None:
        patterns = [
            r"(?:기념품|참가기념품)\s*[:：]?\s*([^.;]{4,80})",
            r"(?:제공품|굿즈)\s*[:：]?\s*([^.;]{4,80})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                gift = match.group(1).strip()
                gift = re.sub(r"\s+", " ", gift)
                return gift[:80]
        return None

    def _extract_course_note(self, text: str) -> str | None:
        lowered = text.casefold()
        if any(keyword in lowered for keyword in ["트레일", "trail", "임도", "산길"]):
            return "공식 페이지 기준 트레일 구간 포함 가능성"
        if any(keyword in lowered for keyword in ["강변", "해변", "바다", "coast", "ocean"]):
            return "공식 페이지 기준 바람 영향을 받을 수 있는 해안/강변형 코스"
        if any(keyword in lowered for keyword in ["공원", "도심", "순환", "loop", "road"]):
            return "공식 페이지 기준 로드 중심 순환 코스"
        return None

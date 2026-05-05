from datetime import date

from app.climate import monthly_climate
from app.schemas.profile import RunnerProfile
from app.schemas.race import RaceDetail, RaceListItem, RaceSearchParams
from app.schemas.recommendation import (
    HomeInsight,
    HomeQuickStats,
    RaceRecommendation,
    RecommendationDetailResponse,
    RecommendationHomeResponse,
    RecommendationResponse,
    TrainingStep,
)
from app.services.profile_service import ProfileService
from app.services.race_service import RaceService


class RecommendationService:
    def __init__(self, race_service: RaceService, profile_service: ProfileService) -> None:
        self.race_service = race_service
        self.profile_service = profile_service

    def get_home_feed(self) -> RecommendationResponse | None:
        profile = self.profile_service.get_primary_profile()
        if profile is None:
            return None

        recommendations = self._build_recommendations(profile)
        return RecommendationResponse(profile=profile, recommendations=recommendations[:8])

    def get_mobile_home(self) -> RecommendationHomeResponse | None:
        profile = self.profile_service.get_primary_profile()
        if profile is None:
            return None

        recommendations = self._build_recommendations(profile)
        hero = recommendations[0] if recommendations else None
        nearby_open_races = [item for item in recommendations if "nearby" in item.fit_labels][:5]
        long_term_matches = [item for item in recommendations if item.training_weeks_left > 12][:5]

        return RecommendationHomeResponse(
            profile=profile,
            hero_recommendation=hero,
            quick_stats=self._build_quick_stats(profile, recommendations),
            next_actions=self._build_next_actions(profile, hero),
            insights=self._build_insights(profile, recommendations, hero),
            training_timeline=self._build_training_timeline(profile),
            nearby_open_races=nearby_open_races,
            long_term_matches=long_term_matches,
        )

    def get_recommendation_detail(self, slug: str) -> RecommendationDetailResponse | None:
        profile = self.profile_service.get_primary_profile()
        race = self.race_service.get_race(slug)
        if profile is None or race is None or race.event_date < date.today():
            return None

        recommendation = self._recommend_race(profile, RaceListItem.model_validate(race.model_dump()), race)
        return RecommendationDetailResponse(
            recommendation=recommendation,
            why_now=self._build_why_now(profile, recommendation),
            caution_notes=self._build_caution_notes(profile, recommendation),
            training_focus=self._build_training_focus(profile, recommendation),
            action_checklist=self._build_action_checklist(recommendation),
        )

    def _build_recommendations(self, profile: RunnerProfile) -> list[RaceRecommendation]:
        races = self.race_service.list_races(RaceSearchParams())
        recommendations = []
        for race in races:
            if race.event_date < date.today():
                continue
            if race.registration_status == "registration_closed":
                continue
            recommendations.append(
                self._recommend_race(profile, race, self.race_service.get_race(race.slug))
            )
        recommendations = [item for item in recommendations if item.score >= 45]
        recommendations.sort(key=lambda item: item.score, reverse=True)
        return recommendations

    def _build_quick_stats(
        self,
        profile: RunnerProfile,
        recommendations: list[RaceRecommendation],
    ) -> HomeQuickStats:
        today = date.today()
        local_matches = sum(1 for item in recommendations if item.race.region == profile.home_region)
        return HomeQuickStats(
            target_distance=profile.target_distance,
            days_until_goal=max((profile.target_event_date - today).days, 0),
            open_races_count=len(recommendations),
            local_match_count=local_matches,
        )

    def _build_next_actions(
        self,
        profile: RunnerProfile,
        hero: RaceRecommendation | None,
    ) -> list[str]:
        actions = [
            f"주 {profile.weekly_run_days}회 기준으로 이번 주 훈련 일정을 확정해보세요",
            "관심 대회 2개를 비교해서 메인 목표와 백업 목표를 나눠보세요",
        ]
        if hero is not None:
            actions.insert(0, f"{hero.race.title} 접수 마감일과 이동 계획을 먼저 확인해보세요")
        return actions[:3]

    def _build_insights(
        self,
        profile: RunnerProfile,
        recommendations: list[RaceRecommendation],
        hero: RaceRecommendation | None,
    ) -> list[HomeInsight]:
        insights: list[HomeInsight] = []
        if hero is not None:
            insights.append(
                HomeInsight(
                    title="오늘의 추천",
                    body=f"{hero.race.title}는 {hero.recommendation_reason}",
                    tone="highlight",
                )
            )

        local_matches = sum(1 for item in recommendations if item.race.region == profile.home_region)
        insights.append(
            HomeInsight(
                title="이동 부담",
                body=f"현재 추천 후보 중 {local_matches}개가 {profile.home_region} 또는 가까운 권역에 있어요.",
                tone="calm",
            )
        )

        if profile.weekly_run_days <= 2:
            body = "주 2회 이하 러닝이면 10km 또는 하프 입문형 대회부터 잡는 편이 안정적이에요."
        elif profile.weekly_run_days <= 4:
            body = "지금 훈련 빈도라면 기록 개선형 하프나 10km 챌린지에 잘 맞아요."
        else:
            body = "훈련 빈도가 좋아서 장거리 목표까지 확장할 준비가 되어 있어요."
        insights.append(
            HomeInsight(
                title="훈련 리듬",
                body=body,
                tone="coach",
            )
        )
        return insights

    def _build_training_timeline(self, profile: RunnerProfile) -> list[TrainingStep]:
        days_until_goal = max((profile.target_event_date - date.today()).days, 0)
        if days_until_goal <= 28:
            current = "taper"
        elif days_until_goal <= 70:
            current = "specific"
        elif days_until_goal <= 120:
            current = "build"
        else:
            current = "base"

        return [
            TrainingStep(
                title="베이스 만들기",
                subtitle="러닝 빈도와 회복 루틴을 안정화하는 단계",
                is_current=current == "base",
            ),
            TrainingStep(
                title="지구력 확장",
                subtitle="롱런과 페이스 감각을 늘리는 단계",
                is_current=current == "build",
            ),
            TrainingStep(
                title="레이스 특화",
                subtitle="목표 거리 기준으로 페이스를 맞추는 단계",
                is_current=current == "specific",
            ),
            TrainingStep(
                title="테이퍼링",
                subtitle="피로를 줄이고 컨디션을 끌어올리는 단계",
                is_current=current == "taper",
            ),
        ]

    def _build_why_now(self, profile: RunnerProfile, recommendation: RaceRecommendation) -> list[str]:
        distance_text = " · ".join(recommendation.race.distances) if recommendation.race.distances else profile.target_distance
        points = [
            f"{recommendation.race.event_date} 개최라 현재 루틴에서 준비 간격을 잡기 좋아요.",
            f"{profile.target_distance} 목표와 {distance_text} 구성이 잘 맞아요.",
            f"{recommendation.course_style} 성격의 코스로 현재 선호 노면은 {recommendation.surface_hint} 쪽에 가까워요.",
        ]
        if "nearby" in recommendation.fit_labels:
            points.append("이동과 숙박 부담이 적어서 훈련 리듬을 해치지 않아요.")
        return points

    def _build_caution_notes(self, profile: RunnerProfile, recommendation: RaceRecommendation) -> list[str]:
        cautions: list[str] = []
        if recommendation.training_weeks_left < 6:
            cautions.append("준비 기간이 짧아서 페이스 욕심보다 완주 전략이 중요해요.")
        if profile.experience_level == "beginner":
            cautions.append("주간 러닝 횟수보다 회복과 부상 관리 비중을 더 높게 잡아주세요.")
        if recommendation.weather_risk == "high":
            cautions.append("계절 변수 때문에 보급, 복장, 페이스 계획을 더 세밀하게 준비해야 해요.")
        if recommendation.cutoff_pressure == "strict":
            cautions.append("컷오프 압박이 있을 수 있으니 훈련 중 목표 페이스 체크가 필요해요.")
        if not cautions:
            cautions.append("현재 조건에서는 큰 리스크가 없지만 접수 마감일과 코스 정보를 다시 확인하세요.")
        return cautions

    def _build_training_focus(self, profile: RunnerProfile, recommendation: RaceRecommendation) -> list[str]:
        focuses = [
            f"주 {profile.weekly_run_days}회 기준으로 1회는 롱런, 1회는 템포 주행으로 구성하기",
            f"{recommendation.race.distances[0]} 페이스를 기준으로 레이스 감각 세션 넣기" if recommendation.race.distances else "목표 거리 기준 페이스 감각 세션 넣기",
            "대회 2주 전부터는 거리보다 회복과 수면 리듬 관리에 집중하기",
        ]
        if recommendation.surface_hint == "trail":
            focuses.append("오르막과 내리막 리듬 적응용 언덕 세션을 넣기")
        if recommendation.weather_risk == "high":
            focuses.append("더위나 추위 적응을 위해 시간대와 복장 테스트를 미리 해보기")
        return focuses

    def _build_action_checklist(self, recommendation: RaceRecommendation) -> list[str]:
        checklist = [
            "접수 마감일 확인하기",
            "출발 장소와 이동 시간 계산하기",
            "레이스 전 주 훈련량 20% 줄이기",
            f"{recommendation.race.title}를 메인 목표 또는 백업 목표로 분류하기",
        ]
        if recommendation.cost_band == "premium":
            checklist.append("참가비와 이동비를 함께 계산해서 예산을 먼저 확정하기")
        return checklist

    def _recommend_race(
        self,
        profile: RunnerProfile,
        race: RaceListItem,
        race_detail: RaceDetail | None = None,
    ) -> RaceRecommendation:
        score = 40
        score_breakdown = {
            "base": 40,
            "location": 0,
            "distance": 0,
            "timing": 0,
            "difficulty": 0,
            "surface": 0,
            "travel": 0,
            "weather": 0,
            "cost": 0,
            "cutoff": 0,
        }
        reasons: list[str] = []
        labels: list[str] = []
        weeks_left = max((race.event_date - date.today()).days // 7, 0)
        difficulty_level = self._estimate_difficulty(race, race_detail)
        surface_hint = self._infer_surface(race)
        course_style = self._infer_course_style(race, surface_hint)
        seasonal_tag = self._seasonal_tag(race.event_date)
        weather_risk = self._weather_risk(race)
        cost_band = self._estimate_cost_band(race, race_detail)
        cost_display = self._format_cost_display(race, race_detail, cost_band)
        cutoff_pressure = self._estimate_cutoff_pressure(race, race_detail)
        target_distance_bucket = self._distance_bucket(profile.target_distance)
        race_distance_bucket = self._longest_distance_bucket(race.distances)

        if race.region == profile.home_region:
            score += 22
            score_breakdown["location"] += 22
            reasons.append("집 근처라 이동 부담이 적어요")
            labels.append("nearby")

        if profile.target_distance in race.distances:
            score += 24
            score_breakdown["distance"] += 24
            reasons.append("목표 거리와 정확히 맞아요")
            labels.append("distance-match")
        elif any(profile.target_distance in distance or distance in profile.target_distance for distance in race.distances):
            score += 12
            score_breakdown["distance"] += 12
            reasons.append("목표 거리와 비슷한 카테고리예요")
            labels.append("distance-close")
        elif race_distance_bucket and target_distance_bucket:
            bucket_gap = abs(race_distance_bucket - target_distance_bucket)
            if bucket_gap == 1:
                score += 6
                score_breakdown["distance"] += 6
                reasons.append("목표 거리 바로 전 단계로 경험 쌓기 좋아요")
                labels.append("distance-build")
            elif bucket_gap >= 2:
                score -= 10
                score_breakdown["distance"] -= 10
                reasons.append("현재 목표와는 거리 차이가 큰 편이에요")
                labels.append("distance-gap")

        if 4 <= weeks_left <= 16:
            score += 18
            score_breakdown["timing"] += 18
            reasons.append("지금부터 준비하기 좋은 일정이에요")
            labels.append("timing-good")
        elif weeks_left < 4:
            score -= 10
            score_breakdown["timing"] -= 10
            reasons.append("준비 기간이 조금 촉박해요")
            labels.append("timing-tight")
        else:
            score += 6
            score_breakdown["timing"] += 6
            reasons.append("중장기 목표로 잡기 좋아요")
            labels.append("timing-long")

        if profile.experience_level == "beginner" and any(tag in race.distances for tag in ["Full", "42.195km", "50km", "100km"]):
            score -= 18
            score_breakdown["difficulty"] -= 18
            reasons.append("첫 목표로는 다소 도전적인 거리예요")
            labels.append("stretch-goal")
        elif profile.experience_level == "beginner" and difficulty_level == "hard":
            score -= 12
            score_breakdown["difficulty"] -= 12
            reasons.append("입문자에게는 난이도가 높은 편이에요")
            labels.append("hard-course")
        elif profile.experience_level == "advanced" and difficulty_level == "hard":
            score += 8
            score_breakdown["difficulty"] += 8
            reasons.append("도전적인 코스를 소화할 준비가 되어 있어요")
            labels.append("challenge-fit")

        if profile.preferred_surface == "trail" and surface_hint == "trail":
            score += 12
            score_breakdown["surface"] += 12
            reasons.append("선호하는 트레일 감성과 잘 맞아요")
            labels.append("surface-match")
        elif profile.preferred_surface == "road" and surface_hint == "road":
            score += 10
            score_breakdown["surface"] += 10
            reasons.append("로드 중심 훈련 루틴과 자연스럽게 이어져요")
            labels.append("surface-match")
        elif profile.preferred_surface != "mixed" and surface_hint != "mixed" and profile.preferred_surface != surface_hint:
            score -= 8
            score_breakdown["surface"] -= 8
            reasons.append("선호 노면과는 조금 다른 편이에요")
            labels.append("surface-mismatch")

        if weather_risk == "high":
            score -= 6
            score_breakdown["weather"] -= 6
            reasons.append("계절상 날씨 변수에 조금 더 대비해야 해요")
            labels.append("weather-watch")
        elif weather_risk == "low":
            score += 4
            score_breakdown["weather"] += 4
            reasons.append("계절 조건이 비교적 안정적인 편이에요")
            labels.append("weather-stable")

        if profile.experience_level == "beginner" and cost_band == "premium":
            score -= 4
            score_breakdown["cost"] -= 4
            reasons.append("입문 첫 대회치고는 비용 부담이 있을 수 있어요")
            labels.append("cost-watch")
        elif profile.experience_level in {"intermediate", "advanced"} and cost_band == "budget":
            score += 3
            score_breakdown["cost"] += 3
            labels.append("value-good")

        if profile.experience_level == "beginner" and cutoff_pressure == "strict":
            score -= 8
            score_breakdown["cutoff"] -= 8
            reasons.append("컷오프 압박이 있을 수 있어 초반 목표로는 보수적 접근이 좋아요")
            labels.append("cutoff-watch")
        elif profile.experience_level == "advanced" and cutoff_pressure == "strict":
            score += 4
            score_breakdown["cutoff"] += 4
            labels.append("competitive-fit")

        if profile.travel_willingness == "local_only" and race.region != profile.home_region:
            score -= 18
            score_breakdown["travel"] -= 18
        elif profile.travel_willingness == "nationwide" and race.region != profile.home_region:
            score += 5
            score_breakdown["travel"] += 5
            labels.append("travel-ok")

        reason = " · ".join(reasons[:3]) if reasons else "훈련 목표와 일정 기준으로 무난한 선택지예요"
        final_score = max(score, 0)
        return RaceRecommendation(
            race=race,
            score=final_score,
            confidence=self._confidence_label(final_score),
            difficulty_level=difficulty_level,
            surface_hint=surface_hint,
            course_style=course_style,
            seasonal_tag=seasonal_tag,
            weather_risk=weather_risk,
            cost_band=cost_band,
            cost_display=cost_display,
            cutoff_pressure=cutoff_pressure,
            recommendation_reason=reason,
            training_weeks_left=weeks_left,
            fit_labels=labels,
            score_breakdown=score_breakdown,
        )

    def _infer_course_style(self, race: RaceListItem, surface_hint: str) -> str:
        text = " ".join([race.title, race.venue]).casefold()
        if surface_hint == "trail":
            return "trail-technical"
        if any(keyword in text for keyword in ["night", "야간", "night run"]):
            return "night-city"
        if any(keyword in text for keyword in ["bridge", "coast", "ocean", "beach", "한강", "해변", "바다"]):
            return "scenic-road"
        if any(keyword in text for keyword in ["park", "공원", "city", "도심"]):
            return "city-loop"
        return "mixed-road"

    def _seasonal_tag(self, event_date: date) -> str:
        month = event_date.month
        if month in {3, 4, 5}:
            return "spring"
        if month in {6, 7, 8}:
            return "summer"
        if month in {9, 10, 11}:
            return "fall"
        return "winter"

    def _weather_risk(self, race: RaceListItem) -> str:
        climate = monthly_climate(race.region, race.event_date.month)
        text = " ".join([race.title, race.venue]).casefold()
        if climate["temp"] >= 27 or climate["temp"] <= 0:
            return "high"
        if climate["rain"] >= 220:
            return "high"
        if any(keyword in text for keyword in ["trail", "산", "오름"]) and climate["rain"] >= 140:
            return "medium"
        if 8 <= climate["temp"] <= 20 and climate["rain"] <= 110:
            return "low"
        return "medium"

    def _estimate_cost_band(self, race: RaceListItem, race_detail: RaceDetail | None = None) -> str:
        if race_detail and race_detail.entry_fee_note:
            fee = self._parse_price(race_detail.entry_fee_note)
            if fee is not None:
                if fee >= 70000:
                    return "premium"
                if fee >= 35000:
                    return "standard"
                return "budget"
        longest_bucket = self._longest_distance_bucket(race.distances) or 1
        text = " ".join([race.title, race.venue]).casefold()
        if "charity" in text or "kids" in text or "어린이" in text:
            return "budget"
        if longest_bucket >= 4 or "trail" in text or "ultra" in text:
            return "premium"
        if longest_bucket >= 2:
            return "standard"
        return "budget"

    def _estimate_cutoff_pressure(self, race: RaceListItem, race_detail: RaceDetail | None = None) -> str:
        if race_detail and race_detail.cutoff_note:
            note = race_detail.cutoff_note.casefold()
            if "2시간" in note or "120분" in note:
                return "strict"
            if "3시간" in note or "180분" in note:
                return "moderate"
        longest_bucket = self._longest_distance_bucket(race.distances) or 1
        text = " ".join([race.title, race.venue]).casefold()
        if longest_bucket >= 4 or "qualifier" in text or "record" in text or "championship" in text:
            return "strict"
        if longest_bucket >= 2:
            return "moderate"
        return "relaxed"

    def _format_cost_display(
        self,
        race: RaceListItem,
        race_detail: RaceDetail | None,
        cost_band: str,
    ) -> str:
        if race_detail and race_detail.entry_fee_note:
            return race_detail.entry_fee_note

        if cost_band == "budget":
            return "2만원대 예상"
        if cost_band == "standard":
            return "4만원대 예상"
        return "7만원 이상 예상"

    def _infer_surface(self, race: RaceListItem) -> str:
        text = " ".join([race.title, race.venue]).casefold()
        trail_keywords = ["trail", "트레일", "산", "forest", "숲", "오름"]
        road_keywords = ["road", "seoul", "city", "bridge", "한강", "공원", "marathon", "run"]
        if any(keyword in text for keyword in trail_keywords):
            return "trail"
        if any(keyword in text for keyword in road_keywords):
            return "road"
        return "mixed"

    def _estimate_difficulty(self, race: RaceListItem, race_detail: RaceDetail | None = None) -> str:
        longest_bucket = self._longest_distance_bucket(race.distances)
        surface_hint = self._infer_surface(race)
        text = " ".join(
            filter(None, [race.title, race.venue, race_detail.course_note if race_detail else None])
        ).casefold()
        hill_keywords = ["trail", "산", "오름", "ultra", "100k", "50k", "sky", "climb", "vertical"]

        if surface_hint == "trail" and any(keyword in text for keyword in hill_keywords):
            return "hard"
        if longest_bucket is not None and longest_bucket >= 4:
            return "hard"
        if longest_bucket is not None and longest_bucket >= 2:
            return "medium"
        return "easy"

    def _distance_bucket(self, distance_label: str) -> int | None:
        value = distance_label.casefold()
        if "100" in value or "ultra" in value:
            return 5
        if "50" in value or "full" in value or "42.195" in value or "42k" in value:
            return 4
        if "half" in value or "21" in value:
            return 3
        if "10" in value:
            return 2
        if "5" in value:
            return 1
        return None

    def _longest_distance_bucket(self, distances: list[str]) -> int | None:
        buckets = [self._distance_bucket(distance) for distance in distances]
        buckets = [bucket for bucket in buckets if bucket is not None]
        if not buckets:
            return None
        return max(buckets)

    def _confidence_label(self, score: int) -> str:
        if score >= 85:
            return "high"
        if score >= 65:
            return "medium"
        return "low"

    def _parse_price(self, note: str) -> int | None:
        digits = "".join(char for char in note if char.isdigit())
        if not digits:
            return None
        return int(digits)

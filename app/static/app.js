const heroCard = document.querySelector("#hero-card");
const statsGrid = document.querySelector("#stats-grid");
const actionList = document.querySelector("#action-list");
const insightStack = document.querySelector("#insight-stack");
const timeline = document.querySelector("#timeline");
const nearbyList = document.querySelector("#nearby-list");
const longtermList = document.querySelector("#longterm-list");
const catalogList = document.querySelector("#catalog-list");
const catalogSummary = document.querySelector("#catalog-summary");
const catalogStatus = document.querySelector("#catalog-status");
const catalogRegion = document.querySelector("#catalog-region");
const catalogSearch = document.querySelector("#catalog-search");
const refreshButton = document.querySelector("#refresh-button");
const refreshStatus = document.querySelector("#refresh-status");
const editProfileButton = document.querySelector("#edit-profile-button");
const statTemplate = document.querySelector("#stat-template");
const raceCardTemplate = document.querySelector("#race-card-template");
const detailPanel = document.querySelector("#detail-panel");
const calendarGrid = document.querySelector("#calendar-grid");
const profileForm = document.querySelector("#profile-form");
const profileStatus = document.querySelector("#profile-status");
const onboardingStatus = document.querySelector("#onboarding-status");
const tabButtons = document.querySelectorAll(".tab-button");
const tabPages = document.querySelectorAll(".tab-page");

let currentHomeData = null;
let currentRaceCatalog = [];
let selectedRecommendation = null;
let selectedRecommendationDetail = null;
let selectedRaceDetail = null;
let isRefreshing = false;

refreshButton.addEventListener("click", () => loadHome({ userInitiated: true }));
editProfileButton.addEventListener("click", () => switchTab("profile-tab"));
tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchTab(button.dataset.tabTarget));
});
profileForm.addEventListener("submit", handleProfileSubmit);
catalogStatus.addEventListener("change", () => loadRaceCatalog());
catalogRegion.addEventListener("change", () => loadRaceCatalog());
catalogSearch.addEventListener("input", handleCatalogSearch);

async function loadHome(options = {}) {
  const { userInitiated = false } = options;
  if (isRefreshing) {
    return;
  }

  setRefreshState(true, userInitiated ? "최신 추천을 다시 불러오는 중이에요..." : "");

  try {
    await loadOnboardingStatus();
    await loadRaceCatalog();
    const response = await fetch("/api/v1/recommendations/me/home", {
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error("추천 홈 데이터를 불러오지 못했습니다.");
    }
    const data = await response.json();
    currentHomeData = data;
    renderHome(data);
    setRefreshState(false, userInitiated ? "최신 추천으로 새로고침했어요." : "");
  } catch (error) {
    setRefreshState(false, "새로고침에 실패했어요. 잠시 후 다시 시도해주세요.");
    renderError(error.message);
    return;
  }
}

function renderHome(data) {
  selectedRecommendation =
    selectedRecommendation &&
    [...data.nearby_open_races, ...data.long_term_matches].find(
      (item) => item.race.slug === selectedRecommendation.race.slug,
    )
      ? [...data.nearby_open_races, ...data.long_term_matches].find(
          (item) => item.race.slug === selectedRecommendation.race.slug,
        )
      : data.hero_recommendation;

  renderHero(data.hero_recommendation, data.profile);
  renderStats(data.quick_stats);
  renderActions(data.next_actions);
  renderInsights(data.insights);
  renderTimeline(data.training_timeline);
  renderRaceRail(nearbyList, data.nearby_open_races, "가까운 조건에 맞는 대회가 아직 충분하지 않아요.");
  renderRaceRail(longtermList, data.long_term_matches, "장기 목표용 후보는 다음 수집 주기에서 더 늘어날 수 있어요.");
  renderDetail(selectedRecommendationDetail, selectedRecommendation, selectedRaceDetail);
  renderCalendar(data.profile, selectedRecommendation);
  hydrateProfileForm(data.profile);
}

function renderHero(hero, profile) {
  if (!hero) {
    heroCard.innerHTML = `
      <p class="hero-kicker">Runner Brief</p>
      <h2>${profile.nickname}님에게 맞는 추천 대회를 더 찾는 중이에요</h2>
      <p class="hero-caption">프로필이나 목표 거리를 바꾸면 더 정확한 제안을 만들 수 있어요.</p>
    `;
    return;
  }

  heroCard.innerHTML = `
    <p class="hero-kicker">Today’s Match</p>
    <h2>${hero.race.title}</h2>
    <div class="hero-meta">
      <span class="hero-pill">${hero.race.region}</span>
      <span class="hero-pill">${hero.race.distances.join(" · ")}</span>
      <span class="hero-pill">${hero.training_weeks_left}주 준비</span>
      <span class="hero-pill">${hero.difficulty_level} 난이도</span>
    </div>
    <p class="hero-caption">${hero.recommendation_reason}</p>
  `;
}

function renderStats(stats) {
  statsGrid.innerHTML = "";
  const entries = [
    ["목표 거리", stats.target_distance],
    ["목표일까지", `${stats.days_until_goal}일`],
    ["지금 열린 후보", `${stats.open_races_count}개`],
    ["지역 매치", `${stats.local_match_count}개`],
  ];

  entries.forEach(([label, value]) => {
    const node = statTemplate.content.firstElementChild.cloneNode(true);
    node.querySelector(".stat-label").textContent = label;
    node.querySelector(".stat-value").textContent = value;
    statsGrid.appendChild(node);
  });
}

function renderActions(actions) {
  actionList.innerHTML = actions
    .map((action) => `<article class="action-item">${action}</article>`)
    .join("");
}

function renderInsights(insights) {
  insightStack.innerHTML = insights
    .map(
      (item) => `
        <article class="insight-card" data-tone="${item.tone}">
          <h4>${item.title}</h4>
          <p>${item.body}</p>
        </article>
      `,
    )
    .join("");
}

function renderTimeline(steps) {
  timeline.innerHTML = steps
    .map(
      (step) => `
        <article class="timeline-step ${step.is_current ? "current" : ""}">
          <h4>${step.title}</h4>
          <p>${step.subtitle}</p>
        </article>
      `,
    )
    .join("");
}

function renderRaceRail(container, races, emptyMessage) {
  container.innerHTML = "";

  if (!races.length) {
    container.innerHTML = `<div class="empty-note">${emptyMessage}</div>`;
    return;
  }

  races.forEach((item) => {
    container.appendChild(
      buildRaceCard({
        region: item.race.region,
        distances: item.race.distances,
        title: item.race.title,
        meta: `${item.race.event_date} · ${item.race.venue} · ${item.confidence} confidence`,
        reason: item.recommendation_reason,
        isBookmarked: item.race.is_bookmarked,
        onBookmark: async () => toggleBookmark(item),
        onSelect: () => selectRecommendation(item),
      }),
    );
  });
}

function renderCatalog(races) {
  currentRaceCatalog = races;
  catalogSummary.textContent = `총 ${races.length}개의 대회를 찾았어요.`;
  catalogList.innerHTML = "";

  if (!races.length) {
    catalogList.innerHTML = `<div class="empty-note">조건에 맞는 대회가 아직 없어요.</div>`;
    return;
  }

  races.forEach((race) => {
    catalogList.appendChild(
      buildRaceCard({
        region: race.region,
        distances: race.distances,
        title: race.title,
        meta: `${race.event_date} · ${race.venue} · ${formatRegistrationStatus(race.registration_status)}`,
        reason: buildCatalogReason(race),
        isBookmarked: race.is_bookmarked,
        onBookmark: async () => toggleCatalogBookmark(race),
        onSelect: () => selectCatalogRace(race),
      }),
    );
  });
}

function buildRaceCard({
  region,
  distances,
  title,
  meta,
  reason,
  isBookmarked,
  onBookmark,
  onSelect,
}) {
  const node = raceCardTemplate.content.firstElementChild.cloneNode(true);
  node.querySelector(".race-region").textContent = region;
  node.querySelector(".race-distance").textContent = distances.join(" · ");
  node.querySelector(".race-title").textContent = title;
  node.querySelector(".race-meta").textContent = meta;
  node.querySelector(".race-reason").textContent = reason;
  const bookmarkButton = node.querySelector(".bookmark-button");
  syncBookmarkButton(bookmarkButton, isBookmarked);
  bookmarkButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    await onBookmark();
  });
  node.addEventListener("click", onSelect);
  node.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onSelect();
    }
  });
  return node;
}

function renderDetail(detail, item, raceDetail) {
  if (!item) {
    detailPanel.innerHTML = `<div class="empty-note">대회를 선택하면 기본 정보와 바로가기 버튼이 보여요.</div>`;
    return;
  }

  const detailSource = raceDetail ?? detail?.recommendation?.race ?? item.race;
  const primaryLink = detailSource.apply_url || detailSource.official_url || detailSource.source_url;
  const actions = buildDetailActions(detailSource);
  const keyNotes = buildDetailNotes(detail, detailSource, item);
  const summary = buildDetailSummary(detailSource.description || item.recommendation_reason);
  const badges = buildDetailBadges(detailSource);

  detailPanel.innerHTML = `
    <div class="detail-head">
      <p class="section-kicker">대회 브리프</p>
      <h4 class="detail-title">${item.race.title}</h4>
      <div class="detail-badges">${badges}</div>
      <div class="detail-lead">
        <p class="detail-summary">${summary}</p>
      </div>
    </div>
    ${actions}
    <div class="detail-grid">
      <article class="detail-box">
        <strong>대회 일정</strong>
        <span>${formatDisplayDate(detailSource.event_date)}</span>
      </article>
      <article class="detail-box">
        <strong>접수 상태</strong>
        <span>${formatRegistrationStatus(detailSource.registration_status)}</span>
      </article>
      <article class="detail-box">
        <strong>장소</strong>
        <span>${detailSource.region} · ${detailSource.venue}</span>
      </article>
      <article class="detail-box">
        <strong>거리</strong>
        <span>${detailSource.distances.join(" · ") || "-"}</span>
      </article>
      <article class="detail-box">
        <strong>접수 기간</strong>
        <span>${formatDateRange(detailSource.registration_open_at, detailSource.registration_close_at)}</span>
      </article>
      <article class="detail-box">
        <strong>시작 시간</strong>
        <span>${detailSource.start_time || "미정"}</span>
      </article>
      <article class="detail-box">
        <strong>주최</strong>
        <span>${detailSource.organizer || "확인 필요"}</span>
      </article>
      <article class="detail-box">
        <strong>참가비</strong>
        <span>${detailSource.entry_fee_note || item.cost_display || "확인 필요"}</span>
      </article>
      <article class="detail-box">
        <strong>문의</strong>
        <span>${formatContact(detailSource.contact_phone, detailSource.contact_email)}</span>
      </article>
      <article class="detail-box">
        <strong>코스 메모</strong>
        <span>${detailSource.course_note || "공식 안내 확인"}</span>
      </article>
    </div>
    <div class="detail-section">
      <strong>확인 포인트</strong>
      <ul class="detail-list">${keyNotes.map((text) => `<li>${text}</li>`).join("")}</ul>
    </div>
    ${primaryLink ? "" : '<div class="empty-note">아직 바로가기 링크를 찾지 못했어요. 출처 링크를 먼저 확인해보세요.</div>'}
  `;
}

function renderCalendar(profile, item) {
  const weeks = buildTrainingWeeks(profile, item);
  calendarGrid.innerHTML = weeks
    .map(
      (week) => `
        <article class="calendar-week ${week.isCurrent ? "current" : ""}">
          <strong>${week.label}</strong>
          <h4>${week.title}</h4>
          <p>${week.body}</p>
        </article>
      `,
    )
    .join("");
}

function buildTrainingWeeks(profile, item) {
  const blocks = [
    "주간 루틴을 고정하고 편한 페이스로 거리 감각을 만들어요.",
    "롱런을 조금씩 늘리고, 1회는 템포 주간으로 구성해요.",
    "목표 거리 기준으로 페이스 훈련 비중을 높여요.",
    "대회 2주 전부터는 피로를 줄이며 컨디션을 끌어올려요.",
  ];
  const distanceText = item ? item.race.distances.join(" · ") : profile.target_distance;
  return Array.from({ length: 12 }, (_, index) => {
    const weekNumber = index + 1;
    const phase = index < 3 ? 0 : index < 6 ? 1 : index < 10 ? 2 : 3;
    return {
      label: `${weekNumber}주차`,
      title: `${distanceText} 대비 ${["베이스", "지구력", "페이스", "테이퍼"][phase]} 단계`,
      body: `주 ${profile.weekly_run_days}회 기준. ${blocks[phase]}`,
      isCurrent: weekNumber === 1,
    };
  });
}

function hydrateProfileForm(profile) {
  Object.entries(profile).forEach(([key, value]) => {
    const input = profileForm.elements.namedItem(key);
    if (!input) {
      return;
    }
    if ((key === "home_region" || key === "target_distance") && input.tagName === "SELECT") {
      ensureSelectOption(input, value);
    }
    input.value = value;
  });
}

function ensureSelectOption(select, value) {
  const hasOption = Array.from(select.options).some((option) => option.value === value);
  if (hasOption) {
    return;
  }

  const fallbackOption = document.createElement("option");
  fallbackOption.value = value;
  fallbackOption.textContent = value;
  select.appendChild(fallbackOption);
}

function formatCutoffPressure(value) {
  if (value === "strict") {
    return "높음";
  }
  if (value === "moderate") {
    return "보통";
  }
  if (value === "relaxed") {
    return "여유 있음";
  }
  return value;
}

async function handleProfileSubmit(event) {
  event.preventDefault();
  profileStatus.textContent = "저장 중...";
  const formData = new FormData(profileForm);
  const payload = Object.fromEntries(formData.entries());
  payload.weekly_run_days = Number(payload.weekly_run_days);

  const response = await fetch("/api/v1/profiles/me", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    profileStatus.textContent = "저장에 실패했어요.";
    return;
  }

  profileStatus.textContent = "프로필을 저장했고 추천을 새로 계산할게요.";
  await loadHome({ userInitiated: true });
}

async function selectRecommendation(item) {
  selectedRecommendation = item;
  const [detail, raceDetail] = await Promise.all([
    loadRecommendationDetail(item.race.slug),
    loadRaceDetail(item.race.slug),
  ]);
  selectedRecommendationDetail = detail;
  selectedRaceDetail = raceDetail;
  renderDetail(selectedRecommendationDetail, item, selectedRaceDetail);
  if (currentHomeData) {
    renderCalendar(currentHomeData.profile, item);
  }
  switchTab("plan-tab");
}

async function selectCatalogRace(race) {
  const [detail, raceDetail] = await Promise.all([
    loadRecommendationDetail(race.slug),
    loadRaceDetail(race.slug),
  ]);
  if (detail?.recommendation) {
    selectedRecommendation = detail.recommendation;
    selectedRecommendationDetail = detail;
    selectedRaceDetail = raceDetail;
    renderDetail(detail, detail.recommendation, raceDetail);
    if (currentHomeData) {
      renderCalendar(currentHomeData.profile, detail.recommendation);
    }
    switchTab("plan-tab");
    return;
  }

  selectedRecommendation = { race, cost_display: raceDetail?.entry_fee_note || "확인 필요" };
  selectedRecommendationDetail = null;
  selectedRaceDetail = raceDetail;
  renderDetail(null, selectedRecommendation, raceDetail);
  switchTab("plan-tab");
}

function switchTab(targetId) {
  tabButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.tabTarget === targetId);
  });
  tabPages.forEach((page) => {
    page.classList.toggle("is-active", page.id === targetId);
  });
}

async function loadRecommendationDetail(slug) {
  const response = await fetch(`/api/v1/recommendations/me/${slug}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

async function loadRaceDetail(slug) {
  const response = await fetch(`/api/v1/races/${slug}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

async function toggleBookmark(item) {
  const nextValue = !item.race.is_bookmarked;
  const response = await fetch(`/api/v1/races/${item.race.slug}/bookmark`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_bookmarked: nextValue }),
  });
  if (!response.ok) {
    return;
  }
  const updated = await response.json();
  item.race.is_bookmarked = updated.is_bookmarked;
  await loadHome({ userInitiated: true });
}

async function toggleCatalogBookmark(race) {
  const response = await fetch(`/api/v1/races/${race.slug}/bookmark`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_bookmarked: !race.is_bookmarked }),
  });
  if (!response.ok) {
    return;
  }
  await loadRaceCatalog();
  if (currentHomeData) {
    await loadHome({ userInitiated: false });
  }
}

function syncBookmarkButton(button, isBookmarked) {
  button.textContent = isBookmarked ? "찜됨" : "찜하기";
  button.classList.toggle("is-bookmarked", isBookmarked);
}

async function loadOnboardingStatus() {
  const response = await fetch("/api/v1/onboarding/status", {
    cache: "no-store",
  });
  if (!response.ok) {
    onboardingStatus.textContent = "온보딩 상태를 불러오지 못했어요.";
    return;
  }
  const data = await response.json();
  onboardingStatus.textContent = data.completed
    ? "프로필 설정이 완료됐어요. 홈에서 오늘의 추천 대회를 바로 확인할 수 있어요."
    : "아직 첫 설정이 끝나지 않았어요. 프로필을 저장하면 추천이 더 정확해져요.";
}

async function loadRaceCatalog() {
  const params = new URLSearchParams();
  if (catalogStatus.value) {
    params.set("status", catalogStatus.value);
  }
  if (catalogRegion.value) {
    params.set("region", catalogRegion.value);
  }
  if (catalogSearch.value.trim()) {
    params.set("q", catalogSearch.value.trim());
  }

  const url = params.toString() ? `/api/v1/races?${params.toString()}` : "/api/v1/races";
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    catalogSummary.textContent = "대회 목록을 불러오지 못했어요.";
    catalogList.innerHTML = `<div class="error-note">잠시 후 다시 시도해주세요.</div>`;
    return;
  }
  const races = await response.json();
  renderCatalog(races);
}

function handleCatalogSearch() {
  window.clearTimeout(handleCatalogSearch.timer);
  handleCatalogSearch.timer = window.setTimeout(() => {
    loadRaceCatalog();
  }, 220);
}

function buildCatalogReason(race) {
  const parts = [];
  if (race.is_bookmarked) {
    parts.push("관심 대회로 저장되어 있어요.");
  }
  if (race.distances.length) {
    parts.push(`${race.distances.join(" · ")} 참가가 가능해요.`);
  }
  parts.push(`${formatRegistrationStatus(race.registration_status)} 상태를 확인해보세요.`);
  return parts.join(" ");
}

function formatRegistrationStatus(value) {
  if (value === "registration_open") {
    return "접수 중";
  }
  if (value === "registration_upcoming") {
    return "오픈 예정";
  }
  if (value === "registration_closed") {
    return "접수 마감";
  }
  return value;
}

function formatDateRange(start, end) {
  if (!start && !end) {
    return "확인 필요";
  }
  if (start && end) {
    return `${formatDisplayDate(start)} ~ ${formatDisplayDate(end)}`;
  }
  return formatDisplayDate(start || end);
}

function buildDetailActions(detailSource) {
  const links = [
    detailSource.apply_url
      ? `<a class="detail-link primary" href="${detailSource.apply_url}" target="_blank" rel="noreferrer">신청하기</a>`
      : "",
    detailSource.official_url
      ? `<a class="detail-link secondary" href="${detailSource.official_url}" target="_blank" rel="noreferrer">공식 사이트 바로가기</a>`
      : "",
  ].filter(Boolean);

  if (!links.length) {
    return "";
  }

  return `<div class="detail-actions">${links.join("")}</div>`;
}

function buildDetailNotes(detail, detailSource, item) {
  const notes = [];
  if (detailSource.cutoff_note) {
    notes.push(`컷오프 정보: ${detailSource.cutoff_note}`);
  }
  if (item?.training_weeks_left) {
    notes.push(`현재 기준 준비 기간은 약 ${item.training_weeks_left}주입니다.`);
  }
  if (detail?.caution_notes?.length) {
    notes.push(...detail.caution_notes.slice(0, 2));
  }
  if (detail?.why_now?.length) {
    notes.push(detail.why_now[0]);
  }
  if (!notes.length) {
    notes.push("접수 마감일, 장소, 공식 신청 페이지를 먼저 확인해보세요.");
  }
  return notes;
}

function buildDetailSummary(text) {
  const fallback = "대회 핵심 정보와 신청 경로를 먼저 확인해보세요.";
  if (!text) {
    return fallback;
  }

  const normalized = text.replace(/\s+/g, " ").trim();
  const cleaned = normalized.split("기념품:")[0].trim();
  if (cleaned.length <= 180) {
    return cleaned;
  }
  return `${cleaned.slice(0, 180).trim()}...`;
}

function buildDetailBadges(detailSource) {
  const badges = [
    { label: formatRegistrationStatus(detailSource.registration_status), tone: "accent" },
    { label: formatDisplayDate(detailSource.event_date) },
    { label: detailSource.distances.join(" · ") || "거리 확인 필요" },
    { label: detailSource.region },
  ];

  return badges
    .filter((badge) => badge.label)
    .map((badge) => `<span class="detail-badge" data-tone="${badge.tone || "default"}">${badge.label}</span>`)
    .join("");
}

function formatDisplayDate(value) {
  if (!value) {
    return "확인 필요";
  }
  const parts = String(value).split("-");
  if (parts.length !== 3) {
    return value;
  }
  return `${parts[0]}.${parts[1]}.${parts[2]}`;
}

function formatContact(phone, email) {
  if (phone && email) {
    return `${phone} / ${email}`;
  }
  return phone || email || "확인 필요";
}

function renderError(message) {
  heroCard.innerHTML = `
    <p class="hero-kicker">Connection Issue</p>
    <h2>홈 데이터를 불러오지 못했어요</h2>
    <p class="hero-caption">${message}</p>
  `;

  [statsGrid, actionList, insightStack, timeline, nearbyList, longtermList].forEach((node) => {
    node.innerHTML = `<div class="error-note">잠시 후 다시 시도해주세요.</div>`;
  });
  detailPanel.innerHTML = `<div class="error-note">추천 상세를 불러오지 못했어요.</div>`;
  calendarGrid.innerHTML = `<div class="error-note">훈련 캘린더를 만들지 못했어요.</div>`;
  onboardingStatus.textContent = "설정 상태를 확인하지 못했어요.";
}

function setRefreshState(nextRefreshing, statusText) {
  isRefreshing = nextRefreshing;
  refreshButton.classList.toggle("is-loading", nextRefreshing);
  refreshButton.disabled = nextRefreshing;
  refreshButton.textContent = nextRefreshing ? "불러오는 중..." : "새로고침";
  refreshStatus.textContent = statusText;
}

loadHome();

CLIMATE_BY_REGION = {
    "서울": {1: {"temp": -2, "rain": 21}, 2: {"temp": 1, "rain": 25}, 3: {"temp": 7, "rain": 46}, 4: {"temp": 13, "rain": 77}, 5: {"temp": 18, "rain": 102}, 6: {"temp": 23, "rain": 133}, 7: {"temp": 27, "rain": 395}, 8: {"temp": 28, "rain": 348}, 9: {"temp": 23, "rain": 169}, 10: {"temp": 16, "rain": 52}, 11: {"temp": 8, "rain": 53}, 12: {"temp": 1, "rain": 25}},
    "경기": {1: {"temp": -3, "rain": 20}, 2: {"temp": 1, "rain": 24}, 3: {"temp": 7, "rain": 42}, 4: {"temp": 13, "rain": 70}, 5: {"temp": 18, "rain": 95}, 6: {"temp": 23, "rain": 128}, 7: {"temp": 27, "rain": 360}, 8: {"temp": 27, "rain": 320}, 9: {"temp": 22, "rain": 150}, 10: {"temp": 15, "rain": 50}, 11: {"temp": 7, "rain": 48}, 12: {"temp": 0, "rain": 24}},
    "경상": {1: {"temp": 2, "rain": 30}, 2: {"temp": 4, "rain": 40}, 3: {"temp": 9, "rain": 65}, 4: {"temp": 15, "rain": 97}, 5: {"temp": 20, "rain": 101}, 6: {"temp": 23, "rain": 152}, 7: {"temp": 27, "rain": 230}, 8: {"temp": 28, "rain": 227}, 9: {"temp": 23, "rain": 153}, 10: {"temp": 17, "rain": 58}, 11: {"temp": 10, "rain": 44}, 12: {"temp": 4, "rain": 27}},
    "경남": {1: {"temp": 3, "rain": 33}, 2: {"temp": 5, "rain": 45}, 3: {"temp": 10, "rain": 78}, 4: {"temp": 15, "rain": 109}, 5: {"temp": 19, "rain": 112}, 6: {"temp": 23, "rain": 170}, 7: {"temp": 27, "rain": 260}, 8: {"temp": 28, "rain": 250}, 9: {"temp": 23, "rain": 176}, 10: {"temp": 17, "rain": 62}, 11: {"temp": 10, "rain": 48}, 12: {"temp": 4, "rain": 29}},
    "부산": {1: {"temp": 4, "rain": 35}, 2: {"temp": 6, "rain": 50}, 3: {"temp": 10, "rain": 88}, 4: {"temp": 14, "rain": 136}, 5: {"temp": 18, "rain": 154}, 6: {"temp": 21, "rain": 214}, 7: {"temp": 25, "rain": 316}, 8: {"temp": 27, "rain": 266}, 9: {"temp": 23, "rain": 176}, 10: {"temp": 18, "rain": 62}, 11: {"temp": 12, "rain": 48}, 12: {"temp": 6, "rain": 25}},
    "제주": {1: {"temp": 7, "rain": 65}, 2: {"temp": 8, "rain": 58}, 3: {"temp": 11, "rain": 90}, 4: {"temp": 15, "rain": 98}, 5: {"temp": 19, "rain": 110}, 6: {"temp": 22, "rain": 170}, 7: {"temp": 26, "rain": 230}, 8: {"temp": 28, "rain": 250}, 9: {"temp": 24, "rain": 190}, 10: {"temp": 19, "rain": 70}, 11: {"temp": 14, "rain": 62}, 12: {"temp": 9, "rain": 55}},
    "강원": {1: {"temp": -4, "rain": 24}, 2: {"temp": -1, "rain": 31}, 3: {"temp": 5, "rain": 54}, 4: {"temp": 12, "rain": 76}, 5: {"temp": 17, "rain": 93}, 6: {"temp": 21, "rain": 125}, 7: {"temp": 25, "rain": 285}, 8: {"temp": 26, "rain": 295}, 9: {"temp": 21, "rain": 138}, 10: {"temp": 14, "rain": 59}, 11: {"temp": 6, "rain": 47}, 12: {"temp": -1, "rain": 28}},
}

DEFAULT_CLIMATE = {1: {"temp": 0, "rain": 25}, 2: {"temp": 2, "rain": 30}, 3: {"temp": 8, "rain": 55}, 4: {"temp": 14, "rain": 85}, 5: {"temp": 19, "rain": 105}, 6: {"temp": 23, "rain": 150}, 7: {"temp": 27, "rain": 300}, 8: {"temp": 28, "rain": 280}, 9: {"temp": 23, "rain": 165}, 10: {"temp": 16, "rain": 60}, 11: {"temp": 9, "rain": 48}, 12: {"temp": 2, "rain": 28}}


def monthly_climate(region: str, month: int) -> dict[str, int]:
    region_data = CLIMATE_BY_REGION.get(region) or CLIMATE_BY_REGION.get(_normalize_region(region))
    if region_data:
        return region_data[month]
    return DEFAULT_CLIMATE[month]


def _normalize_region(region: str) -> str:
    if "서울" in region:
        return "서울"
    if "경기" in region:
        return "경기"
    if "경남" in region:
        return "경남"
    if "경상" in region or "대구" in region or "울산" in region or "부산" in region:
        return "경상"
    if "제주" in region:
        return "제주"
    if "강원" in region:
        return "강원"
    return region

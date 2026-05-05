from enum import StrEnum


class RaceRegion(StrEnum):
    SEOUL = "서울"
    GYEONGGI = "경기"
    CHUNGCHEONG = "충청"
    GYEONGSANG = "경상"
    JEOLLA = "전라"
    JEJU = "제주"
    GANGWON = "강원"
    OVERSEAS = "해외"


class RegistrationStatus(StrEnum):
    UPCOMING = "registration_upcoming"
    OPEN = "registration_open"
    CLOSED = "registration_closed"


class EventStatus(StrEnum):
    UPCOMING = "upcoming"
    FINISHED = "finished"

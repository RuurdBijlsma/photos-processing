from enum import StrEnum, auto


class EventType(StrEnum):
    # Personal Celebrations
    WEDDING = auto()
    BIRTHDAY = auto()
    ANNIVERSARY = auto()
    GRADUATION = auto()
    BABY_SHOWER = auto()
    HOUSEWARMING = auto()

    # Social and Entertainment
    PARTY = auto()
    CONCERT = auto()
    FESTIVAL = auto()
    NIGHTCLUB = auto()
    MOVIE_NIGHT = auto()

    # Formal and Professional
    CONFERENCE = auto()
    WORKSHOP = auto()
    MEETING = auto()
    SEMINAR = auto()
    CORPORATE_EVENT = auto()

    # Religious and Cultural
    FUNERAL = auto()
    RELIGIOUS_CEREMONY = auto()
    CULTURAL_CELEBRATION = auto()
    CHRISTMAS = auto()
    HALLOWEEN = auto()
    NEW_YEAR = auto()

    # Sports and Competitions
    SPORTS_GAME = auto()
    TOURNAMENT = auto()
    MARATHON = auto()

    # Community and Public
    CHARITY_EVENT = auto()
    PROTEST = auto()
    PARADE = auto()
    EXHIBITION = auto()
    CARNIVAL = auto()

    # Other
    TRIP = auto()
    PICNIC = auto()
    REUNION = auto()
    DATE = auto()
    WORK_EVENT = auto()

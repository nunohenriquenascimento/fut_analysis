from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    COACH = "COACH"
    VIEWER = "VIEWER"


class PlayerPosition(StrEnum):
    GR = "GR"
    DC = "DC"
    ALA = "ALA"
    MDC = "MDC"
    MC = "MC"
    PL = "PL"
    UNIVERSAL = "UNIVERSAL"


class MatchStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    FIRST_HALF = "FIRST_HALF"
    HALF_TIME = "HALF_TIME"
    SECOND_HALF = "SECOND_HALF"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"


class EventTeam(StrEnum):
    US = "US"
    OPPONENT = "OPPONENT"


class EventType(StrEnum):
    GOAL = "GOAL"
    OWN_GOAL = "OWN_GOAL"
    SHOT_ON_TARGET = "SHOT_ON_TARGET"
    SHOT_OFF_TARGET = "SHOT_OFF_TARGET"
    SHOT_BLOCKED = "SHOT_BLOCKED"
    CORNER = "CORNER"
    FREE_KICK = "FREE_KICK"
    FOUL = "FOUL"
    YELLOW_CARD = "YELLOW_CARD"
    RED_CARD = "RED_CARD"
    OFFSIDE = "OFFSIDE"
    SUBSTITUTION = "SUBSTITUTION"
    PENALTY = "PENALTY"
    SAVE = "SAVE"

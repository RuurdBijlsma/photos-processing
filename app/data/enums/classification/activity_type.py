from enum import StrEnum, auto


class ActivityType(StrEnum):
    # Sports
    RUNNING = auto()
    SWIMMING = auto()
    CYCLING = auto()
    SOCCER = auto()
    BASKETBALL = auto()
    TENNIS = auto()
    BASEBALL = auto()
    SKATEBOARDING = auto()
    SURFING = auto()
    SKIING = auto()
    SNOWBOARDING = auto()
    GOLF = auto()
    HIKING = auto()
    CLIMBING = auto()
    KAYAKING = auto()

    # Fitness and Exercise
    YOGA = auto()
    PILATES = auto()
    WEIGHTLIFTING = auto()
    AEROBICS = auto()
    CROSSFIT = auto()

    # Creative Arts
    DANCING = auto()
    PAINTING = auto()
    DRAWING = auto()
    PHOTOGRAPHY = auto()
    WRITING = auto()
    SCULPTING = auto()

    # Leisure and Hobbies
    READING = auto()
    GARDENING = auto()
    COOKING = auto()
    BAKING = auto()
    FISHING = auto()
    BOARD_GAMES = auto()

    # Social and Events
    TRAVELING = auto()
    CAMPING = auto()
    BARBECUE = auto()
    SHOPPING = auto()

    # Water Activities
    DIVING = auto()
    SNORKELING = auto()
    ROWING = auto()
    WAKEBOARDING = auto()
    SAILING = auto()

    # Other
    WORKING = auto()
    STUDYING = auto()
    RELAXING = auto()
    MEDITATING = auto()

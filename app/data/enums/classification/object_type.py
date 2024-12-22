from enum import StrEnum, auto


class ObjectType(StrEnum):
    FOOD = auto()
    CAR = auto()
    BOAT = auto()
    PLANE = auto()
    PAINTING = auto()
    SCULPTURE = auto()
    DEVICE = ("a device, such as a remote, or speakers, or a monitor, or a computer, "
              "or any other technological device.")
    CLOTHING = auto()
    DRINK = "A glass, jug, bottle or cup to drink from"
    SPORTS = "sports equipment"
    DOCUMENT = auto()
    TOY = auto()

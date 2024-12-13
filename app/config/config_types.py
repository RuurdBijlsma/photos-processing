from enum import StrEnum, auto


class LLMProvider(StrEnum):
    MINICPM = auto()
    OPENAI = auto()
    INTERN_VL = auto()


class CaptionerProvider(StrEnum):
    MINICPM = auto()
    OPENAI = auto()
    INTERN_VL = auto()
    BLIP = auto()

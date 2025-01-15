from enum import StrEnum, auto


class LLMProvider(StrEnum):
    MINICPM = auto()
    OPENAI = auto()


class CaptionerProvider(StrEnum):
    MINICPM = auto()
    OPENAI = auto()
    BLIP = auto()

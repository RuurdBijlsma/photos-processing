from enum import StrEnum, auto


class LLMProvider(StrEnum):
    MINICPM = auto()
    OPENAI = auto()

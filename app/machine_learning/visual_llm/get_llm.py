from app.config.config_types import LLMProvider
from app.machine_learning.visual_llm.MiniCPMLLM import MiniCPMLLM
from app.machine_learning.visual_llm.OpenAILLM import OpenAILLM
from app.machine_learning.visual_llm.VisualLLMProtocol import VisualLLMProtocol


def get_llm_by_provider(provider: LLMProvider) -> VisualLLMProtocol:
    return {
        LLMProvider.MINICPM: MiniCPMLLM,
        LLMProvider.OPENAI: OpenAILLM,
    }[provider]()

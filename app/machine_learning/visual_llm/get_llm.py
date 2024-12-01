from app.config.config_types import LLMProvider
from app.machine_learning.visual_llm.mini_cpm_llm import MiniCPMLLM
from app.machine_learning.visual_llm.openai_llm import OpenAILLM
from app.machine_learning.visual_llm.visual_llm_protocol import VisualLLMProtocol


def get_llm_by_provider(provider: LLMProvider) -> VisualLLMProtocol:
    return {
        LLMProvider.MINICPM: MiniCPMLLM,
        LLMProvider.OPENAI: OpenAILLM,
    }[provider]()

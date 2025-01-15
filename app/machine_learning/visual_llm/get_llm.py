from app.config.config_types import LLMProvider
from app.machine_learning.visual_llm.base_visual_llm import BaseVisualLLM
from app.machine_learning.visual_llm.mini_cpm_llm import MiniCPMLLM
from app.machine_learning.visual_llm.openai_llm import OpenAILLM

llm_providers: dict[LLMProvider, type[BaseVisualLLM]] = {
    LLMProvider.MINICPM: MiniCPMLLM,
    LLMProvider.OPENAI: OpenAILLM,
}


def get_llm_by_provider(provider: LLMProvider) -> BaseVisualLLM:
    return llm_providers[provider]()

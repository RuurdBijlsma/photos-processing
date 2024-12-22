from app.config.config_types import CaptionerProvider, LLMProvider
from app.machine_learning.caption.blip_captioner import BlipCaptioner
from app.machine_learning.caption.captioner_protocol import CaptionerProtocol
from app.machine_learning.caption.llm_captioner import LLMCaptioner


def get_captioner_by_provider(provider: CaptionerProvider) -> CaptionerProtocol:
    return {
        CaptionerProvider.MINICPM: lambda: LLMCaptioner(LLMProvider.MINICPM),
        CaptionerProvider.OPENAI: lambda: LLMCaptioner(LLMProvider.OPENAI),
        CaptionerProvider.BLIP: BlipCaptioner,
    }[provider]()

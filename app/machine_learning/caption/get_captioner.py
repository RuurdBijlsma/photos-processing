from app.config.config_types import LLMProvider, CaptionerProvider
from app.machine_learning.caption.BlipCaptioner import BlipCaptioner
from app.machine_learning.caption.CaptionerProtocol import CaptionerProtocol
from app.machine_learning.caption.LLMCaptioner import LLMCaptioner


def get_captioner_by_provider(provider: CaptionerProvider) -> CaptionerProtocol:
    return {
        CaptionerProvider.MINICPM: lambda: LLMCaptioner(LLMProvider.MINICPM),
        CaptionerProvider.OPENAI: lambda: LLMCaptioner(LLMProvider.OPENAI),
        CaptionerProvider.BLIP: BlipCaptioner
    }[provider]()

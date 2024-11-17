from PIL.Image import Image

from app.data.interfaces.visual_information import EmbeddingVisualInformation, \
    OcrVisualInformation
from app.machine_learning.embedding.CLIPEmbedder import CLIPEmbedder
from app.machine_learning.ocr.ResnetTesseractOCR import ResnetTesseractOCR
from app.machine_learning.visual_llm.MiniCPMVisualLLM import MiniCPMVisualLLM

embedder = CLIPEmbedder()

ocr = ResnetTesseractOCR()
llm = MiniCPMVisualLLM()


def frame_ocr(
    visual_info: EmbeddingVisualInformation,
    pil_image: Image
) -> OcrVisualInformation:
    has_text = ocr.has_legible_text(pil_image)
    extracted_text: str | None = None
    summary: str | None = None
    # boxes: list[OCRBox] | None = None
    if has_text:
        extracted_text = ocr.get_text(pil_image)
        if extracted_text.strip() == "":
            has_text = False
            extracted_text = None
        # boxes = ocr.get_boxes(pil_image)

    # Check if this could be a photo of a document
    if has_text and extracted_text and len(extracted_text) > 65:
        prompt = """Analyze the image and provide the following details:

            Summary: A concise summary of the content in the photo, including any key points or important sections visible.
            Text Detection: Detect and list any legible text visible in the image. If possible, extract it and provide a short excerpt or the full text.
            Language Detection: Identify the language(s) in the text and specify the primary language used.
            Document Type: Determine the type of document or text. Is it a formal document (e.g., letter, contract, form), informal (e.g., note, memo), or something else? Provide details about the document's likely purpose (e.g., invoice, receipt, report, etc.).
            Text Formatting: If relevant, describe any specific formatting styles such as headings, bullet points, numbered lists, tables, or signatures.
            Additional Features: Detect if there are any images, logos, or other non-text elements present that provide additional context or information about the document (e.g., company logos, photos, charts).
            Contextual Details: If applicable, mention any visible date, address, or other contextual information that could help understand the document’s origin or purpose."""

        summary = llm.image_question(pil_image, prompt)

    return OcrVisualInformation(
        **visual_info.model_dump(),
        has_legible_text=has_text,
        ocr_text=extracted_text,
        document_summary=summary
        # ocr_boxes=boxes
    )

import base64
from io import BytesIO

from PIL import Image
from llama_cpp import Llama
from llama_cpp.llama_chat_format import MiniCPMv26ChatHandler


def image_to_base64_data_uri(file_path):
    with Image.open(file_path) as img:
        resized = img.resize((int(img.width / 1280 * 720), 720))
        buffer = BytesIO()
        resized.save(buffer, format="JPEG")
        base_64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{base_64_data}"


# Replace with the actual path to your image file in WSL
file_path = "./data/images/1/20170819_100607.jpg"
data_uri = image_to_base64_data_uri(file_path)

# Initialize the chat handler
chat_handler = MiniCPMv26ChatHandler(
    clip_model_path="./scripts/model/minicpm/mmproj-model-f16.gguf"
)

# Initialize the Llama model
llm = Llama(
    model_path="./scripts/model/minicpm/ggml-model-Q6_K.gguf",
    chat_handler=chat_handler,
    n_ctx=2048,  # Increase context window to accommodate the image embedding
)

# Create the messages for the chat completion
messages = [
    {
        "role": "system",
        "content": "You are great at identifying objects in images, you keep you answers to a comma separated list of objects.",
    },
    {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": data_uri}},
            {
                "type": "text",
                "text": "What are the main objects visible in this photo? (e.g., dog, car, table)?",
            },
        ],
    },
]

# Generate the response
response = llm.create_chat_completion(messages=messages)
print(response)
print()
print(response["choices"][0]["message"]["content"])

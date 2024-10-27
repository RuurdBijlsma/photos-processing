from llama_cpp import Llama

llm = Llama(
    model_path="./scripts/model/Llama-3.2-3B-Instruct-Q6_K.gguf",
    n_gpu_layers=-1, # Uncomment to use GPU acceleration
    # seed=1337, # Uncomment to set a specific seed
    n_ctx=2048, # Uncomment to increase the context window
)
chat_prefix = "Keep your answers short and direct, ideally one sentence."
conversation = [chat_prefix]

while True:
    question = input("User:")
    conversation.append(f"User: {question}\nAssistant: ")
    output = llm(
        "\n".join(conversation),
        max_tokens=None,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
        stop=["User:"],  # Stop generating just before the model would generate a new question
        echo=False  # Echo the prompt back in the output
    )
    response = output["choices"][0]["text"]
    conversation.append(response)
    print(f"Assistant: {response}")
    print("CONVERSATION")
    print("\n".join(conversation))

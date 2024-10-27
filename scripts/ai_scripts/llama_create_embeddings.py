import llama_cpp

llm = llama_cpp.Llama(model_path="scripts/model/Llama-3.2-3B-Instruct-Q6_K.gguf", embedding=True,
                      pooling_type=llama_cpp.LLAMA_POOLING_TYPE_MEAN)

embeddings = llm.create_embedding(["Hello, world!"])

print(embeddings)

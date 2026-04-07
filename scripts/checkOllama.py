import ollama

response = ollama.chat(model="minimax-m2.5:cloud", messages=[{"role": "user", "content": "Hello"}])
print(response)
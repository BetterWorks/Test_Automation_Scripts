from ollama import Client

client = Client(host='http://localhost:11434')

def generate_from_ollama(prompt: str):
    response = client.complete(prompt)
    return response  # Modify as needed based on response structure

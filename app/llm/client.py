import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mistral"

def call_llm(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "num_predict": 120,
            "temperature": 0.2
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]

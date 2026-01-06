import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt: str) -> str:
    if not client.api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=400,
        timeout=10.0,
        # CRITICAL FIX: This forces the model to output valid JSON every time
        response_format={"type": "json_object"} 
    )

    return response.choices[0].message.content
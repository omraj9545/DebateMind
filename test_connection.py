# test_connection.py — delete after verifying Groq connectivity
from groq import Groq
from config import GROQ_API_KEY, MODELS

client = Groq(api_key=GROQ_API_KEY)
resp = client.chat.completions.create(
    model=MODELS["against"],
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
    max_tokens=30
)
print(resp.choices[0].message.content)

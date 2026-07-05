import re, time
from app.agents import groq_client, load_prompt, groq_retry
from config import MODELS, MAX_TOKENS, TEMPERATURE

def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks from Qwen model output."""
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

SYSTEM_PROMPT = load_prompt("pro")

@groq_retry
async def _call_groq(messages: list) -> str:
    response = await groq_client.chat.completions.create(
        model=MODELS["pro"],
        messages=messages,
        max_tokens=1024,
        temperature=TEMPERATURE["pro"],
    )
    return response.choices[0].message.content.strip()

async def run_pro_agent(topic: str) -> tuple[str, float]:
    """Returns (argument_text, latency_seconds)."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Motion: {topic}"}
    ]
    start = time.perf_counter()
    result = await _call_groq(messages)
    return _strip_think_tags(result), round(time.perf_counter() - start, 2)

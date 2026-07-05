import re, time
from app.agents import groq_client, load_prompt, groq_retry
from config import MODELS, MAX_TOKENS, TEMPERATURE

def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

SYSTEM_PROMPT = load_prompt("fact_checker")

@groq_retry
async def _call_groq(messages: list) -> str:
    response = await groq_client.chat.completions.create(
        model=MODELS["fact"],
        messages=messages,
        max_tokens=1024,
        temperature=TEMPERATURE["fact"],
    )
    return response.choices[0].message.content.strip()

async def run_fact_checker(topic: str, pro: str, against: str) -> tuple[str, float]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": (
            f"Debate topic: {topic}\n\n"
            f"PRO ARGUMENT:\n{pro}\n\n"
            f"AGAINST ARGUMENT:\n{against}"
        )}
    ]
    start = time.perf_counter()
    result = await _call_groq(messages)
    return _strip_think_tags(result), round(time.perf_counter() - start, 2)

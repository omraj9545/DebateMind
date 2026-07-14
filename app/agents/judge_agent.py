import json, re, time
from app.agents import groq_client, load_prompt, groq_retry
from config import MODELS, MAX_TOKENS, TEMPERATURE

def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()

SYSTEM_PROMPT = load_prompt("judge")

@groq_retry
async def _call_groq(messages: list) -> str:
    response = await groq_client.chat.completions.create(
        model=MODELS["judge"],
        messages=messages,
        max_tokens=1500,
        temperature=TEMPERATURE["judge"],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content.strip()

def _parse_json(raw: str) -> dict:
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end   = cleaned.rfind("}") + 1
        return json.loads(cleaned[start:end])

async def run_judge(
    topic: str, pro: str, against: str, fact_check: str
) -> tuple[dict, float]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": (
            f"Topic: {topic}\n\n"
            f"PRO:\n{pro}\n\n"
            f"AGAINST:\n{against}\n\n"
            f"FACT CHECK:\n{fact_check}"
        )}
    ]
    start = time.perf_counter()
    raw = await _call_groq(messages)
    raw = _strip_think_tags(raw)
    latency = round(time.perf_counter() - start, 2)
    return _parse_json(raw), latency

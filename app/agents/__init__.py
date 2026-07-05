import asyncio
from pathlib import Path
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import GROQ_API_KEY, MAX_RETRIES, RETRY_WAIT_MIN, RETRY_WAIT_MAX, PROMPT_DIR

# Async Groq client — one instance shared across all agents
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

def load_prompt(name: str) -> str:
    """Load a prompt from prompts/<name>.txt at startup."""
    path = Path(PROMPT_DIR) / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()

# Retry decorator — wraps every Groq API call
def groq_retry(func):
    return retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(
            multiplier=1,
            min=RETRY_WAIT_MIN,
            max=RETRY_WAIT_MAX
        ),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )(func)

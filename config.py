import os
from dotenv import load_dotenv

load_dotenv()

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Models — sourced from .env so swapping needs zero code changes
MODELS = {
    "pro":     os.getenv("PRO_MODEL",     "qwen/qwen3.6-27b"),
    "against": os.getenv("AGAINST_MODEL", "llama-3.3-70b-versatile"),
    "fact":    os.getenv("FACT_MODEL",    "qwen/qwen3.6-27b"),
    "judge":   os.getenv("JUDGE_MODEL",   "llama-3.3-70b-versatile"),
}

# Agent settings
MAX_TOKENS       = int(os.getenv("MAX_TOKENS", 400))
TEMPERATURE = {
    "pro":     float(os.getenv("TEMPERATURE_PRO",     0.7)),
    "against": float(os.getenv("TEMPERATURE_AGAINST", 0.75)),
    "fact":    float(os.getenv("TEMPERATURE_FACT",    0.3)),
    "judge":   float(os.getenv("TEMPERATURE_JUDGE",   0.2)),
}

# Retry
MAX_RETRIES    = int(os.getenv("MAX_RETRIES",    3))
RETRY_WAIT_MIN = int(os.getenv("RETRY_WAIT_MIN", 1))
RETRY_WAIT_MAX = int(os.getenv("RETRY_WAIT_MAX", 8))

# Paths
LOG_DIR     = os.getenv("LOG_DIR",     "logs")
HISTORY_DIR = os.getenv("HISTORY_DIR", "history")
PROMPT_DIR  = os.getenv("PROMPT_DIR",  "prompts")

# Ensure directories exist
import pathlib
pathlib.Path(LOG_DIR).mkdir(exist_ok=True)
pathlib.Path(HISTORY_DIR).mkdir(exist_ok=True)

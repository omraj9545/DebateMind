import json, asyncio
from datetime import datetime, timezone
from pathlib import Path
import aiofiles
from config import LOG_DIR, MODELS

async def log_debate(debate_id: str, state: dict) -> None:
    """Write a structured JSON log for one completed debate."""
    record = {
        "debate_id":  debate_id,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "topic":      state["topic"],
        "models":     MODELS,
        "latency": {
            "pro":         state["pro"]["latency"],
            "against":     state["against"]["latency"],
            "fact_check":  state["fact_check"]["latency"],
            "judge":       state["verdict_latency"],
            "total":       state["total_latency"],
        },
        "outputs": {
            "pro_argument":     state["pro"]["content"],
            "against_argument": state["against"]["content"],
            "fact_check":       state["fact_check"]["content"],
        },
        "verdict": state["verdict"],
    }
    path = Path(LOG_DIR) / f"debate_{debate_id}.json"
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(record, indent=2, ensure_ascii=False))

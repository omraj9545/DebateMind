import json
from datetime import datetime, timezone
from pathlib import Path
import aiofiles
from config import HISTORY_DIR

async def save_history(debate_id: str, topic: str, verdict: dict, total_latency: float) -> None:
    record = {
        "debate_id":     debate_id,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "topic":         topic,
        "winner":        verdict.get("winner"),
        "verdict":       verdict.get("verdict"),
        "scores":        verdict.get("scores"),
        "total_latency": total_latency,
    }
    path = Path(HISTORY_DIR) / f"debate_{debate_id}.json"
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(record, indent=2, ensure_ascii=False))

async def list_history(limit: int = 20) -> list[dict]:
    """Return the most recent N debates from history, newest first."""
    files = sorted(
        Path(HISTORY_DIR).glob("debate_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:limit]
    results = []
    for f in files:
        async with aiofiles.open(f, encoding="utf-8") as fp:
            results.append(json.loads(await fp.read()))
    return results

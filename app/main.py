import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.models.schemas import DebateRequest, DebateResponse
from app.graph.workflow import debate_graph
from app.utils.logger import log_debate
from app.utils.history import save_history, list_history
from config import MODELS

app = FastAPI(
    title="DebateMind API",
    description="Multi-agent debate system using LangGraph and Groq",
    version="2.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "DebateMind", "version": "2.0.0"}

@app.post("/debate", response_model=DebateResponse)
async def run_debate(request: DebateRequest, x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
    debate_id = str(uuid.uuid4())[:8]
    user_id = x_user_id or "default_user"
    initial_state = {
        "topic":           request.topic,
        "pro":             None,
        "against":         None,
        "fact_check":      None,
        "verdict":         None,
        "verdict_latency": None,
        "total_latency":   None,
        "debate_id":       debate_id,
        "error":           None,
        "status":          "starting"
    }
    try:
        result = await debate_graph.ainvoke(initial_state)
        v = result["verdict"]

        # Run file logging and history saving as background tasks (fire-and-forget)
        import asyncio
        asyncio.create_task(log_debate(debate_id, result, user_id))
        asyncio.create_task(save_history(
            debate_id, request.topic, v, result["total_latency"], user_id
        ))

        return DebateResponse(
            debate_id         = debate_id,
            topic             = request.topic,
            pro_argument      = result["pro"]["content"],
            against_argument  = result["against"]["content"],
            fact_check        = result["fact_check"]["content"],
            winner            = v["winner"],
            verdict           = v["verdict"],
            scores            = v["scores"],
            key_turning_point = v.get("key_turning_point"),
            timing            = {
                "pro":        result["pro"]["latency"],
                "against":    result["against"]["latency"],
                "fact_check": result["fact_check"]["latency"],
                "judge":      result["verdict_latency"],
                "total":      result["total_latency"],
            },
            models            = MODELS
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(limit: int = 20, x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
    user_id = x_user_id or "default_user"
    return await list_history(user_id=user_id, limit=limit)

@app.get("/debate/{debate_id}", response_model=DebateResponse)
async def get_debate(debate_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
    import json
    from pathlib import Path
    from config import LOG_DIR
    
    user_id = x_user_id or "default_user"
    path = Path(LOG_DIR) / f"debate_{user_id}_{debate_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Debate log not found.")
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        v = data["verdict"]
        lat = data["latency"]
        outputs = data["outputs"]
        
        return DebateResponse(
            debate_id         = data["debate_id"],
            topic             = data["topic"],
            pro_argument      = outputs["pro_argument"],
            against_argument  = outputs["against_argument"],
            fact_check        = outputs["fact_check"],
            winner            = v["winner"],
            verdict           = v["verdict"],
            scores            = v["scores"],
            key_turning_point = v.get("key_turning_point"),
            timing            = {
                "pro":        lat["pro"],
                "against":    lat["against"],
                "fact_check": lat["fact_check"],
                "judge":      lat["judge"],
                "total":      lat["total"],
            },
            models            = data.get("models", MODELS)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the static frontend directory.html
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")


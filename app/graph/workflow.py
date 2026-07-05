import asyncio, uuid
from langgraph.graph import StateGraph, END
from app.graph.state import DebateState
from app.agents.pro_agent     import run_pro_agent
from app.agents.against_agent import run_against_agent
from app.agents.fact_checker  import run_fact_checker
from app.agents.judge_agent   import run_judge

async def pro_node(state: DebateState) -> dict:
    content, latency = await run_pro_agent(state["topic"])
    return {"pro": {"content": content, "latency": latency}, "status": "pro_done"}

async def against_node(state: DebateState) -> dict:
    content, latency = await run_against_agent(
        state["topic"], state["pro"]["content"]
    )
    return {"against": {"content": content, "latency": latency}, "status": "against_done"}

async def fact_check_node(state: DebateState) -> dict:
    content, latency = await run_fact_checker(
        state["topic"],
        state["pro"]["content"],
        state["against"]["content"]
    )
    return {"fact_check": {"content": content, "latency": latency}, "status": "fact_done"}

async def judge_node(state: DebateState) -> dict:
    verdict, latency = await run_judge(
        state["topic"],
        state["pro"]["content"],
        state["against"]["content"],
        state["fact_check"]["content"]
    )
    total = round(
        state["pro"]["latency"] +
        state["against"]["latency"] +
        state["fact_check"]["latency"] +
        latency, 2
    )
    return {
        "verdict":         verdict,
        "verdict_latency": latency,
        "total_latency":   total,
        "status":          "complete"
    }

def build_debate_graph():
    graph = StateGraph(DebateState)
    graph.add_node("pro",        pro_node)
    graph.add_node("against",    against_node)
    graph.add_node("fact_check", fact_check_node)
    graph.add_node("judge",      judge_node)
    graph.set_entry_point("pro")
    graph.add_edge("pro",        "against")
    graph.add_edge("against",    "fact_check")
    graph.add_edge("fact_check", "judge")
    graph.add_edge("judge",      END)
    return graph.compile()

debate_graph = build_debate_graph()

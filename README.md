# DebateMind — Multi-Agent AI Debate Orchestrator

> An asynchronous, state-driven multi-agent debate system built with LangGraph, FastAPI, and Groq. It simulates a structured academic debate on any topic, timings each agent, fact-checks claims, and delivers a formatted score card.

---

## 🚀 Deployed Link
*   **Live Demo:** Deployed on Render (insert your Render URL here)
*   **API Documentation:** `https://your-app-url.onrender.com/docs` (Swagger UI)

---

## 🛠️ Tech Stack & Badges

![Python 3.11](https://img.shields.io/badge/Python-3.11-black?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-State%20Machine-black?style=for-the-badge&logo=chainlink&logoColor=white)
![Groq](https://img.shields.io/badge/Groq%20API-Fast%20Inference-black?style=for-the-badge&logo=fastapi&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Endpoints-black?style=for-the-badge&logo=fastapi&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployment-black?style=for-the-badge&logo=render&logoColor=white)

---

## 📐 Architecture & Workflow

DebateMind coordinates a linear directed acyclic graph (DAG) where conversation state, latency metrics, and responses are propagated sequentially.

```
                  [User Inputs Topic]
                           │
                           ▼
                  [FastAPI Endpoint]
                           │
                           ▼
             ┌───────────────────────────┐
             │   LangGraph Coordinator   │
             │   (State: DebateState)    │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │       Node 1: PRO         │  ──► Model: Qwen-32B
             └─────────────┬─────────────┘
                           │ [Argument State]
             ┌─────────────▼─────────────┐
             │     Node 2: AGAINST       │  ──► Model: Llama-3.3-70B
             └─────────────┬─────────────┘
                           │ [Full Transcript]
             ┌─────────────▼─────────────┐
             │    Node 3: FACT CHECK     │  ──► Model: Qwen-27B
             └─────────────┬─────────────┘
                           │ [Logic Report]
             ┌─────────────▼─────────────┐
             │       Node 4: JUDGE       │  ──► Model: Llama-4-Scout (JSON Verdict)
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │      Output compiler      │
             └─────────────┬─────────────┘
                           ├──────────────────────────────┐
                           ▼                              ▼
                 [Write logs/ debate]            [Write history/ summary]
                           │                              │
                           ▼                              ▼
                     (Async Task)                   (Async Task)
```

---

## 🤖 Agent Model Rationale

Each node in the state machine is powered by a model best suited for its cognitive role:

| Agent Node | Active Model | Cognitive Rationale | Temperature |
| :--- | :--- | :--- | :--- |
| **Pro Agent** | `qwen/qwen3-32b` | Outstanding structured, numbered reasoning; confident, assertive arguing tone. | `0.70` |
| **Against Agent** | `llama-3.3-70b-versatile` | Highly conversational, responsive rebuttal generation; excellent at direct contextual critiques. | `0.75` |
| **Fact Checker** | `qwen/qwen3.6-27b` | Low temperature analytical precision. Focuses strictly on logical fallacies and data consistency. | `0.30` |
| **Judge Agent** | `meta-llama/llama-4-scout-17b-16e-instruct` | Excellent JSON output alignment. Consolidates multi-modal data and outputs clean scorecard matrices. | `0.20` |

---

## 📂 Project Structure

```
debatemind/
├── .env.example            # Sample secrets and model setup
├── .gitignore              # Protects .env, logs/ and history/
├── requirements.txt        # Package requirements
├── render.yaml             # Render infrastructure-as-code deployment layout
├── config.py               # Central config compiler
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI App (Endpoints /health, /debate, /history)
│   ├── agents/
│   │   ├── __init__.py     # Async Groq Client + Tenacity retry decorator
│   │   ├── pro_agent.py    # FOR node
│   │   ├── against_agent.py# AGAINST node
│   │   ├── fact_checker.py # LOGIC node
│   │   └── judge_agent.py  # VERDICT node
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py        # LangGraph TypedDict definition
│   │   └── workflow.py     # Graph creation and compiler
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py      # Pydantic Request/Response validation shapes
│   └── utils/
│       ├── __init__.py
│       ├── logger.py       # Full state debate log parser
│       └── history.py      # Lightweight history list database writer
├── prompts/
│   ├── pro.txt
│   ├── against.txt
│   ├── fact_checker.txt
│   └── judge.txt
├── frontend/
│   ├── index.html          # Minimalist dashboard layout
│   ├── style.css           # Grayscale serif CSS rules
│   └── app.js              # DOM operations & history loaders
├── logs/                   # Auto-created; debate JSON logs (gitignored)
└── history/                # Auto-created; user summaries (gitignored)
```

---

## 🛠️ Local Installation & Deployment

### 1. Prerequisite Conda Environment
```bash
conda create -n debatemind python=3.11 -y
conda activate debatemind
```

### 2. Dependency Installation
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Config
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here

# Models
PRO_MODEL=qwen/qwen3-32b
AGAINST_MODEL=llama-3.3-70b-versatile
FACT_MODEL=qwen/qwen3.6-27b
JUDGE_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

# Agent Parameters
MAX_TOKENS=400
TEMPERATURE_PRO=0.7
TEMPERATURE_AGAINST=0.75
TEMPERATURE_FACT=0.3
TEMPERATURE_JUDGE=0.2

# Path Parameters
LOG_DIR=logs
HISTORY_DIR=history
PROMPT_DIR=prompts
```

### 4. Running the Dev Server (Frontend & Backend)
The FastAPI app mounts the `/frontend` directory statically to the root URL `/`. Running the backend Uvicorn command automatically serves the web UI dashboard and APIs on the same port.

```bash
uvicorn app.main:app --reload --port 8000
```
Visit **`http://localhost:8000/`** in your browser to load the interactive web client.

---

## 🌐 Production API Endpoints

### `GET /health`
Verifies server health.
*   **Response:** `{"status": "ok", "service": "DebateMind", "version": "2.0.0"}`

### `POST /debate`
Orchestrates a new debate run from user topic.
*   **Request Payload:**
    ```json
    { "topic": "Should space exploration be funded by governments?" }
    ```
*   **Response Payload:** Returns full `pro_argument`, `against_argument`, `fact_check`, scores, verdict, and latency metrics.

### `GET /history`
Returns a list of past debate summaries.

### `GET /debate/{debate_id}`
Fetches the full argument logs for a specific debate.

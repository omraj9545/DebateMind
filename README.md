# DebateMind — Multi-Agent AI Debate Orchestrator

> An asynchronous, state-driven multi-agent debate system built with LangGraph, FastAPI, and Groq. It simulates a structured academic debate on any topic, timings each agent, fact-checks claims, and delivers a formatted score card.

---

## 🚀 Deployed Link
*   **Live Demo:** Deployed via Docker container on Render (insert your Render URL here)
*   **API Documentation:** `https://your-app-url.onrender.com/docs` (Swagger UI)

---

## 🛠️ Tech Stack & Badges

![Python 3.11](https://img.shields.io/badge/Python-3.11-black?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-State%20Machine-black?style=for-the-badge&logo=chainlink&logoColor=white)
![Groq](https://img.shields.io/badge/Groq%20API-Fast%20Inference-black?style=for-the-badge&logo=fastapi&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Endpoints-black?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerization-black?style=for-the-badge&logo=docker&logoColor=white)
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

## 🎨 Minimalist Editorial UI
The frontend is designed with a **high-contrast, grayscale editorial theme** using the classic **Times New Roman** serif font family. It resembles a prestigious academic journal or an editorial column, featuring:
*   Sharp 1px structural borders (no colorful curves or glows).
*   Clean, thin progress loader line showing system node states in real-time.
*   Grayscale scorecards mapping agent comparisons side-by-side.
*   **Debate Ledger:** Clickable past debate cards that fetch complete archives directly from database logs.

---

## 💡 System Design Highlights

*   **Config-Driven Architecture:** Model identifiers, max token boundaries, temperatures, and paths are entirely defined in `.env` and initialized via [config.py](config.py). Zero hardcoding.
*   **Externalized Prompts:** Prompts are stored in plain `.txt` files under `/prompts`. Editing prompts does not require redeploying backend logic.
*   **Asynchronous Engine:** Fully async I/O writing logs/history in the background (`asyncio.create_task` + `aiofiles`) to reduce API response blocking.
*   **Retry Middleware:** Automatic exponential backoff on Groq completions using the `tenacity` retry wrapper, handling network hiccups and rate limiting gracefully.
*   **Qwen Think-Tag Stripper:** Integrates custom preprocessing to strip out chain-of-thought `<think>` tags, preventing token budget leakage and ensuring clean JSON parsing.

---

## 📂 Project Structure

```
debatemind/
├── .env.example            # Sample secrets and model setup
├── .gitignore              # Protects .env, logs/ and history/
├── requirements.txt        # Package requirements
├── Dockerfile              # Container building directives
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

## 🛠️ Local Installation

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

### 4. Running the Dev Server
```bash
uvicorn app.main:app --reload --port 8000
```
Visit **`http://localhost:8000/`** to interact with the dashboard, or **`http://localhost:8000/docs`** to see raw schemas.

---

## 🐳 Docker Containerization
Build the container image:
```bash
docker build -t debatemind .
```
Run the container:
```bash
docker run -p 8000:8000 --env-file .env debatemind
```

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

document.addEventListener("DOMContentLoaded", () => {
    const debateForm = document.getElementById("debate-form");
    const topicInput = document.getElementById("topic-input");
    const submitBtn = document.getElementById("submit-btn");
    const loader = document.getElementById("loader");
    const loaderStatus = document.getElementById("loader-status");
    const progressIndicator = document.getElementById("progress-indicator");
    const resultsDashboard = document.getElementById("results-dashboard");
    const historyList = document.getElementById("history-list");

    // Retrieve or generate unique user_id for session isolation
    const userId = getOrCreateUserId();

    function getOrCreateUserId() {
        let id = localStorage.getItem("debatemind_user_id");
        if (!id) {
            id = 'usr_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            localStorage.setItem("debatemind_user_id", id);
        }
        return id;
    }

    // Load history on load
    loadHistory();

    // Submit Debate Form
    debateForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const topic = topicInput.value.trim();
        if (!topic) return;

        // Reset UI
        resultsDashboard.classList.add("hidden");
        loader.classList.remove("hidden");
        submitBtn.disabled = true;
        topicInput.disabled = true;

        // Trigger Loading Progress Animation
        runLoaderAnimation();

        try {
            const response = await fetch("/debate", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-User-ID": userId
                },
                body: JSON.stringify({ topic })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Failed to compile debate workflow.");
            }

            const data = await response.json();
            displayResults(data);
            loadHistory(); // Reload history ledger
        } catch (error) {
            alert("Error running debate: " + error.message);
        } finally {
            loader.classList.add("hidden");
            submitBtn.disabled = false;
            topicInput.disabled = false;
        }
    });

    // Fake progress loading texts to keep user engaged during multi-agent calls
    function runLoaderAnimation() {
        const statuses = [
            { text: "Summoning Agent Council...", pct: 15 },
            { text: "Invoking Pro Agent (Qwen 32B)...", pct: 35 },
            { text: "Drafting Counterarguments (Llama 70B)...", pct: 55 },
            { text: "Analyzing Logic Errors (Qwen 27B)...", pct: 75 },
            { text: "Drafting Verdict & Scores (Llama Scout)...", pct: 90 },
            { text: "Finalizing Output Verdict...", pct: 98 }
        ];

        let index = 0;
        progressIndicator.style.width = "5%";
        loaderStatus.textContent = statuses[0].text;

        const interval = setInterval(() => {
            if (index < statuses.length - 1) {
                index++;
                loaderStatus.textContent = statuses[index].text;
                progressIndicator.style.width = statuses[index].pct + "%";
            } else {
                clearInterval(interval);
            }
        }, 1500);

        // Keep reference to clear if request returns fast
        loader.dataset.intervalId = interval;
    }

    // Populate Results Dashboard
    function displayResults(data) {
        // Clear status animation intervals
        if (loader.dataset.intervalId) {
            clearInterval(parseInt(loader.dataset.intervalId));
        }

        // Header Metadata
        document.getElementById("res-debate-id").textContent = `#${data.debate_id}`;
        document.getElementById("res-topic").textContent = data.topic;
        document.getElementById("res-total-time").textContent = `${data.timing.total}s`;

        // Card Content, Model, Latency mappings
        setAgentCard("pro", data.pro_argument, data.models?.pro, data.timing.pro);
        setAgentCard("against", data.against_argument, data.models?.against, data.timing.against);
        setAgentCard("fact", data.fact_check, data.models?.fact, data.timing.fact_check);
        
        // Judge Card setup
        document.getElementById("judge-model").textContent = formatModelName(data.models?.judge);
        document.getElementById("judge-latency").textContent = `${data.timing.judge}s`;
        
        const winnerBadge = document.getElementById("verdict-winner");
        winnerBadge.textContent = data.winner;
        winnerBadge.className = `winner-name winner-${data.winner.toLowerCase()}`;
        document.getElementById("verdict-text").textContent = data.verdict;
        document.getElementById("verdict-turning-point").textContent = data.key_turning_point || "No specific turning point reported.";

        // Build scoring rows
        buildScoresGrid(data.scores);

        // Show Dashboard
        resultsDashboard.classList.remove("hidden");
        resultsDashboard.scrollIntoView({ behavior: "smooth" });
    }

    function setAgentCard(id, content, model, latency) {
        document.getElementById(`${id}-model`).textContent = formatModelName(model);
        document.getElementById(`${id}-latency`).textContent = `${latency}s`;
        document.getElementById(`${id}-body`).innerHTML = formatMarkdown(content);
    }

    // Simple markdown formatting replacement for cards
    function formatMarkdown(text) {
        if (!text) return "";
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^- (.*?)$/gm, '• $1');
        return formatted;
    }

    function formatModelName(modelString) {
        if (!modelString) return "LLM Model";
        // Convert paths like "meta-llama/llama-3.3-70b-versatile" to simpler representation
        const parts = modelString.split("/");
        return parts[parts.length - 1];
    }

    // Build comparative score bars
    function buildScoresGrid(scores) {
        const grid = document.getElementById("scores-grid");
        grid.innerHTML = ""; // Clear

        Object.keys(scores).forEach(metric => {
            const val = scores[metric];
            const proVal = val.pro;
            const againstVal = val.against;

            const row = document.createElement("div");
            row.className = "score-row";
            row.innerHTML = `
                <div class="score-labels">
                    <span class="score-label">${metric.replace(/_/g, " ")}</span>
                    <span>Pro: ${proVal}% | Against: ${againstVal}%</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-fill pro-fill" style="width: ${proVal * 0.5}%"></div>
                    <div class="score-fill against-fill" style="width: ${againstVal * 0.5}%"></div>
                </div>
            `;
            grid.appendChild(row);
        });
    }

    // Load debate ledger from backend API
    async function loadHistory() {
        try {
            const response = await fetch("/history", {
                headers: { "X-User-ID": userId }
            });
            if (!response.ok) return;

            const data = await response.json();
            if (data.length === 0) {
                historyList.innerHTML = '<div class="no-history">No debates recorded yet.</div>';
                return;
            }

            historyList.innerHTML = "";
            data.forEach(item => {
                const card = document.createElement("div");
                card.className = "history-card glass-panel";
                
                // Format relative date
                const date = new Date(item.timestamp).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });

                card.innerHTML = `
                    <div class="history-card-header">
                        <span>#${item.debate_id}</span>
                        <span>${date}</span>
                    </div>
                    <h4 class="history-card-topic" title="${item.topic}">${item.topic}</h4>
                    <div class="history-card-footer">
                        <span class="history-winner-tag winner-${item.winner.toLowerCase()}">${item.winner} Winner</span>
                        <span class="history-latency">${item.total_latency}s</span>
                    </div>
                `;
                
                // Allow reloading debate when clicked
                card.addEventListener("click", () => loadSpecificDebate(item.debate_id));
                historyList.appendChild(card);
            });
        } catch (error) {
            console.error("Failed to load history ledger:", error);
        }
    }

    // Load full debate details from history log on click
    async function loadSpecificDebate(debateId) {
        try {
            // Re-use current backend's list endpoint or custom loader (since logs contain full outputs)
            // But history endpoint doesn't have full arguments. We can fetch logs directly or add a utility load.
            // Let's create an endpoint on fastapi side, or simulate it. Wait! Let's check how main.py works.
            // FastAPI does not have a GET /debate/{id} endpoint yet. We can load history directly.
            // But history file is smaller. Let's add GET /logs/{id} or simply make GET /history return full info or load logs.
            // Actually, we can fetch logs if they are stored.
            // Let's modify main.py to support fetching full details or check if history has it.
            // Oh, history JSON files *only* have topic, winner, verdict, scores, total_latency.
            // Full log files (logs/debate_<id>.json) have outputs.pro_argument, against_argument, fact_check, and verdict.
            // Let's add a GET /debate/{debate_id} route to app/main.py. This makes the frontend ledger fully interactive!
            const res = await fetch(`/debate/${debateId}`, {
                headers: { "X-User-ID": userId }
            });
            if (!res.ok) {
                alert("Failed to retrieve full debate logs from disk.");
                return;
            }
            const data = await res.json();
            displayResults(data);
        } catch (err) {
            alert("Error loading log: " + err.message);
        }
    }
});

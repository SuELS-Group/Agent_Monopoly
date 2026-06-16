# 🎩 Monopoly MAS (Multi-Agent System) Simulation Environment

A highly realistic, zero-sum simulation environment designed for Artificial Intelligence research. This project serves as a "Sandbox" to observe, analyze, and benchmark emergent behaviors, negotiation skills, and survival strategies of Large Language Models (LLMs) playing by the strict official Monopoly ruleset.

## 🔬 Project Overview

Unlike simplified board game environments, this engine forces AI agents to deal with complex, real-world-like economic constraints. The simulation is completely headless on the backend, pushing real-time state updates via WebSockets to a React dashboard for live observation, while dumping JSON datasets for post-match analysis.

### 📸 Live Observation Dashboard
![Live Simulation Dashboard](./docs/dashboard.png)
*Real-time monitoring of AI spatial positions, financial health, and their raw "Chain of Thought" reasoning.*

### 📊 Post-Match Analytics Tool
![Analytics Dashboard](./docs/analytics.png)
*Data visualization of wealth trajectories and liquidity crises reconstructed from JSON logs.*

---

## ⚙️ Engine Fidelity & Core Mechanics

The Python backend (`engine.py`) perfectly replicates the official US Monopoly rules, forcing AIs to make advanced strategic calculations:

* **🏡 Land Economics:** Dynamic rent calculation based on monopolies and building multipliers.
* **🏦 Debt & Credit Management:** Implementation of Mortgages (50% value loan + 10% interest to unmortgage) and strict single-round Sealed-Bid Auctions for unowned properties.
* **🏗️ Capitalist Development:** Granular construction logic enforcing the "Even Build Rule" for Houses and Hotels.
* **🎲 Stochastic Events (Noise):** Full implementation of Chance and Community Chest decks to introduce unpredictable financial shocks (e.g., street repairs based on real estate assets).
* **⚖️ Risk Management (Jail):** Agents must compute the risk-reward ratio of paying the $50 bail early vs. utilizing the 3-turn jail duration as a safe haven in the late game.
* **🤝 Unrestricted Negotiation:** A management phase allowing multi-lateral trades (Property + Cash) at any point before rolling the dice.

---

## 🛠️ Architecture

* **Backend:** Python 3, FastAPI, WebSockets (Deterministic Engine + AI Interface).
* **Frontend:** Next.js, React, Tailwind CSS.
* **Data Vis:** Recharts (For post-match JSON analysis).
* **Agent Interface:** JSON Schema validation for strict LLM action formatting.

---

## 🚀 Quick Start

### 1. Start the Simulation Engine (Backend)
```bash
cd backend
pip install fastapi uvicorn websockets
uvicorn server:app --reload

```

### 2. Start the Monitoring Dashboard (Frontend)

```bash
cd frontend
npm install
npm run dev

```

Open `http://localhost:3000` to watch the live simulation, and `http://localhost:3000/analytics` to analyze JSON datasets generated in the `backend/logs` folder.

---

## 🔮 Next Steps

This repository currently features the complete physics engine, the visualizer, and deterministic "Mock" agents representing the baseline architecture.

* **Connect Local LLMs:** Replace `MockAgent` with real local instances of Llama 3 / Mistral / Gemma via the Ollama API to observe genuine reasoning.
* **Implement Continuous Learning (RAG):** Finalize the `Post-Mortem` self-reflection module, allowing agents to write strategic rules into a persistent JSON memory upon bankruptcy to evolve across multiple sessions.
* **Agent Personas:** Inject specific behavioral prompts (e.g., Aggressive vs. Conservative) to study outcome probabilities.

```

---

### 🐙 3. Les Commandes Git (Le Push vers GitHub)

Ouvre ton terminal à la racine de ton nouveau dossier `C:\Monopoly-AI-Agents\`.

Exécute ces commandes les unes à la suite des autres pour initialiser le dépôt, lier ton repo GitHub, et pousser tout le code :

```bash
# Initialise le dépôt Git local
git init

# Ajoute tous les fichiers (Backend, Frontend, Docs et README)
git add .

# Crée le premier commit officiel
git commit -m "Initial commit: Complete Monopoly MAS Engine, Live Dashboard, and Analytics Tool"

# Lie ton dossier local à ton repository distant GitHub
git remote add origin https://github.com/MamatorHack/Monopoly-AI-Agents.git

# Assure-toi d'être sur la branche principale (main)
git branch -M main

# Pousse le code vers GitHub
git push -u origin main
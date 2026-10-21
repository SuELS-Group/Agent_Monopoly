# AegntMonopoly
Agent Monopoly is a zero-sum Multi-Agent System (MAS) in which Large Language Models play Monopoly against each other under the official ruleset. Every decision (buying, bidding, building, mortgaging, trading, paying bail, charging rent) is made by a local LLM through Ollama. The engine logs each agent's private reasoning next to public message, so how different models plan, negotiate and bluff can be observed.

![Game Board and Wealth Tracking](docs/game_board.png)
*Figure 1: Real-time board state, monopoly visualization and wealth tracking. The streets are renamed after places in Oldenburg ([name mapping](docs/game_board_name.txt)).*

![Post-Match Behavioral Analytics](docs/game_analytics.png)
*Figure 2: Post-match analytics: wealth trajectories and an LLM-generated behavioral report.*

## Architecture

* **Physics Engine (Backend):** A deterministic Python engine enforcing the rules (mortgages, sealed-bid auctions, even-build rule, jail, cards). A circuit breaker caps the number of management actions per turn, so an agent can never loop forever. With a fixed seed, dice and card draws are fully reproducible.
* **Cognitive Layer (LLMs):** Agents powered by local LLMs (Qwen 3, DeepSeek-R1, Gemma 4, Mistral) via the Ollama REST API.
* **Observation Dashboard (Frontend):** Next.js/React interface for live monitoring, live chain-of-thought tracking, auto-play and post-match analysis.

## Key Features

1. **Player Personas:** Each agent can be given a personality that shapes how it plays and talks, e.g. *Neutral AI*, *Wall Street Shark*, *Cooperative Diplomat*, *Conservative Steward*, *Zen Drifter* or *Independent Monopoly Builder*. Every answer has two parts: private reasoning (`chain_of_thought`) and a public message to the other players (`public_message`), so you can compare what an agent thinks with what it says.

2. **Structured State Report:** Before every decision, the engine sends the agent a structured snapshot of the game instead of a long text history: its own cash and position (`your_agent`), every opponent's cash, position and jail status (`opponents_overview`), the owner, buildings and mortgage status of every property (`market_overview`), and the space it is deciding about. Every turn of the game is also saved as a snapshot in `game_session_*.json` for later analysis.

3. **Hallucination Detection:** Every answer is checked before the engine acts on it. Invented property IDs, properties the agent does not own, malformed trade offers, text instead of numbers and broken JSON are all caught. The move becomes a safe *pass*, the reason is written to the game log (e.g. `Hallucination prevented`, `[LLM DEBUG]`), and the game continues without crashing.

4. **Legal Action Validation:** For each moment, the engine computes the actions that are allowed by the rules and lists them in the prompt (`legal_actions`), e.g. *buy* only if the agent can afford it, *build* only on a full color group and evenly, *mortgage* only without buildings, *trade* only with players still in the game. Any action outside this list is rejected. A circuit breaker caps the management actions per turn, so an agent can never loop forever.

5. **Visual Web Dashboard:** Set up a game in the browser (models, personas, temperature, seed) and play it *step by step* or with *Auto-Play*, watching the board, each player's wealth, and every agent's thoughts and messages live. After the game, the *Analytics* page shows the wealth trajectories and, on request, a behavioral report written by Llama-3.1-70B (bluffing, alliances and rent waivers, persona adherence and the move that decided the game).

## Experiments

All experiments are defined in [`backend/run_experiments.py`](backend/run_experiments.py) and run headless (no browser needed). Every game has 4 players, temperature 0.0 and a fixed seed, so a game can be replayed exactly.

| Series | Experiment groups | Games | Question |
|---|---|---|---|
| **Persona** | `Conservative`, `Gemma_Diplomat`, `DeepSeek_Independent`, `Qwen_Zen` | 4 | Does a persona change behavior? Player 1 gets a persona, the other three are "Neutral AI". |
| **Series 0, Batch 1** | `S0A_Qwen`, `S0B_DeepSeek`, `S0C_Gemma`, `S0D_Mistral` | 20 | Model **family**: four identical players of one model (`qwen3:8b`, `deepseek-r1:8b`, `gemma4:12b`, `mistral-nemo:12b`). |
| **Series 0, Batch 2** | `S0E_Qwen`, `S0F_DeepSeek`, `S0G_Gemma`, `S0H_Mistral` and their `...Mirror` versions | 40 | Model **size**: 2 large + 2 small models of the same family at one table. The Mirror versions swap the large and small seats. |
| **Series 1** | `S1A_DeepSeek`, `S1B_Gemma`, `S1C_Qwen`, `S1D_Mistral` | 20 | Mixed table: one large model of each family. The seating rotates, so each model holds seat 1 in one group. |

Series 0 and Series 1 use seeds 42-46 (one game per seed), so each group has 5 games. The persona experiments use seed 42.

**Models** (pull them with `ollama pull <tag>` before running):

| Family | Large | Small |
|---|---|---|
| Qwen | `qwen3:32b` | `qwen3:8b` |
| DeepSeek | `deepseek-r1:32b` | `deepseek-r1:8b` |
| Gemma | `gemma4:26b` (Series 1: `gemma4:31b`) | `gemma4:12b` |
| Mistral | `mistral-small:24b` | `mistral-nemo:12b` |

Each experiment pulls in only the models it uses; `python run_experiments.py --list` shows the models of every game.

## Installation

You need [Ollama](https://ollama.com/download) and a GPU that can run the models you choose.

```bash
# 1. Clone the repository
git clone https://github.com/SuELS-Group/Agent_Monopoly.git
cd Agent_Monopoly

# 2. Create the Python environment
conda create -n monopoly python=3.12 -y
conda activate monopoly
pip install -r requirements.txt

# 3. Pull the models (example: the ones for Series 0 Batch 1)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull gemma4:12b
ollama pull mistral-nemo:12b
```

The code expects Ollama at `http://localhost:11434`. If Ollama runs on another machine, either forward the port over SSH (see [Running the web dashboard](#running-the-web-dashboard)) or point to it directly:

```bash
export OLLAMA_URL=http://<your-ollama-host>:11434/api/generate
```

## Running the Experiments

Always run from inside `backend/`, so `rules.json` and `logs/` are found:

```bash
cd backend

# List all experiments (add --filter or --only to narrow the list)
python run_experiments.py --list

# Run one persona experiment (needs mistral-small:24b)
python run_experiments.py --only 1B_Conservative_Temp00_seed42

# Run all of Series 0 Batch 1 (S0A-S0D, 20 games)
python run_experiments.py --filter '^S0[A-D]'
```

More options:

| Command | What it does |
|---|---|
| `--filter '^S0[E-H]'` | Series 0 Batch 2 (S0E-S0H plus Mirror) |
| `--filter '^S1'` | Series 1 |
| `--filter '^1B_'` | All persona experiments |
| `--max-turns 5` | Quick smoke test (stop after 5 turns) |
| `--analyze` | Also write the Llama-3.1-70B behavioral report (optional, needs `llama3.1:70b`) |

For long batches, run the command inside `tmux` or `screen` so it keeps going after you log out.

**Output** (in `backend/logs/`, where `<tag>` = `<experiment>_<timestamp>_seed<N>`):

| File | Content |
|---|---|
| `game_session_<tag>.json` | One snapshot per turn: board, players and the game log (decisions, private thoughts, public messages) |
| `wealth_<tag>.csv` | Net worth of each player per turn |
| `report_<experiment>.html` | Behavioral report (only with `--analyze`) |

## Running the Web Dashboard

The dashboard lets you configure agents in the browser, watch a game live and analyze finished games. You need Node.js 20.9 or newer.

**1. Connect to Ollama (only if it runs on a remote GPU server)**
Forward the server's Ollama port to your machine. Keep this terminal open:
```bash
ssh -L 11434:localhost:11434 <your_username>@<your-gpu-server>
```
If Ollama runs on your own machine, skip this step.

**2. Start the game engine (backend)**
In a new terminal:
```bash
conda activate monopoly
cd backend
uvicorn server:app --reload
```
The engine listens on `http://localhost:8000`.

**3. Start the dashboard (frontend)**
In another terminal:
```bash
cd frontend
npm install
npm run dev
```

**4. Play**
Open `http://localhost:3000`. Add agents (up to 6), pick a model and persona for each, optionally set a temperature and a seed, then start the game with *Step Turn* or *Auto-Play*. Every model you choose must be pulled in Ollama first.

**5. Analyze a game**
Open `http://localhost:3000/analytics`, upload a `game_session_*.json` file from `backend/logs/` and click *Request behavioral analysis* (needs `llama3.1:70b` in Ollama).

## License

Apache License 2.0, see [LICENSE](LICENSE).

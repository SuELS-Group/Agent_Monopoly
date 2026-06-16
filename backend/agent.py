import json
import os

MONOPOLY_SYSTEM_PROMPT = """
You are an autonomous AI agent participating in a strict and competitive simulation of the official Monopoly game.

[ABSOLUTE OBJECTIVE]
Your sole goal is to maximize your capital, bankrupt all your opponents, and be the last player standing. This is a zero-sum game: there is no room for mercy.

[OFFICIAL GAME RULES - NO EXCEPTIONS]
1. THE BOARD: You receive $200 when passing Go.
2. ECONOMY: A monopoly (owning all streets of one color) doubles the rent of unimproved properties.
3. CONSTRUCTION: You must own a full color monopoly to build houses.
4. NEGOTIATION: You can propose trades at any time (Properties + Cash). Bluffing is allowed.
5. BANKRUPTCY: If you owe more money than you can pay, you are eliminated and hand over your properties to the creditor.

[RESPONSE FORMAT]
You MUST analyze the situation in a "chain_of_thought" block to justify your anticipations and risk calculations before defining your "action".
"""

class MockAgent:
    def __init__(self, agent_id: int, name: str, persona: str = "balanced"):
        self.agent_id = agent_id
        self.name = name
        self.persona = persona
        self.memory_file = f"memory_{self.name.lower()}.json"
        self.memory = self._load_memory()

    def _load_memory(self) -> list:
        """Loads lessons from previous games from the disk."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_memory(self, lesson: str) -> None:
        """Saves a new lesson to the disk."""
        self.memory.append(lesson)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    def build_system_prompt(self) -> str:
        """Merges immutable rules with the agent's learned lessons."""
        memory_text = "\n".join([f"- {m}" for m in self.memory]) if self.memory else "No past experience."
        return f"{MONOPOLY_SYSTEM_PROMPT}\n\n[YOUR PAST LESSONS (Learned the hard way)]\n{memory_text}"

    def trigger_post_mortem(self, fatal_logs: list) -> None:
        """
        Called by the Engine when the agent goes bankrupt.
        Asks the AI to analyze its death and extract a strategic rule.
        """
        system_prompt = "You were just eliminated in Monopoly. Analyze the recent logs to understand your fatal mistake. Formulate ONLY ONE concise strategic rule (max 2 sentences) that you will apply in future games."
        user_prompt = json.dumps(fatal_logs, indent=2, ensure_ascii=False)
        
        # --- LLM RESPONSE SIMULATION (To be replaced by Ollama call) ---
        simulated_lesson = "I went bankrupt because I kept no liquidity after my purchases. Rule for the future: Always keep a safety net equivalent to the highest rent on the board."
        
        print(f"\n💀 [POST-MORTEM] {self.name} is analyzing its defeat...")
        print(f"💡 Lesson learned: {simulated_lesson}\n")
        
        self._save_memory(simulated_lesson)

    def query_llm(self, prompt_json: str) -> dict:
        """Mock method to simulate AI actions including auctions."""
        state = json.loads(prompt_json)
        agent_id = state["your_agent"]["id"]
        balance = state["your_agent"]["balance"]
        action_required = state.get("action_required")

        # --- 0. JAIL DECISION LOGIC ---
        if action_required == "jail_decision":
            # Check if board is dangerous (someone has hotels)
            hotels_on_board = sum(1 for s in state["market_overview"] if s.get("buildings", 0) == 5 and s["owner_id"] != agent_id)
            
            if hotels_on_board > 0 and balance < 1000:
                return {
                    "chain_of_thought": "The board is too dangerous right now with hotels, and I am not rich. I will use Jail as a free safe house.",
                    "action": "wait"
                }
            elif balance >= 50:
                return {
                    "chain_of_thought": "I have enough money and need to buy properties or collect rent. I will pay the $50 bail.",
                    "action": "pay_bail"
                }
            else:
                return {
                    "chain_of_thought": "I don't have $50 to spare. I will wait and hope for a double.",
                    "action": "wait"
                }
        
        # --- 1. AUCTION LOGIC ---
        if action_required == "auction_bid":
            base_price = state["space_details"]["base_price"]
            
            # If the AI has plenty of cash, try to get a bargain (60% of base price)
            if balance >= base_price:
                bid_amount = int(base_price * 0.6)
                return {
                    "chain_of_thought": f"I have ${balance}. I will try to snipe {state['space_details']['name']} at a discount for ${bid_amount}.",
                    "action": "bid",
                    "bid": bid_amount
                }
            # If poor, try a desperate lowball offer
            elif balance > 20:
                return {
                    "chain_of_thought": "I am low on cash but will place a $10 minimum bid just in case nobody else wants it.",
                    "action": "bid",
                    "bid": 10
                }
            else:
                return {
                    "chain_of_thought": "I have no money for this auction.",
                    "action": "pass",
                    "bid": 0
                }

        # --- 2. REGULAR BUY LOGIC ---
        if action_required == "buy_property":
            # Adding a bit of randomness so they don't buy EVERYTHING, triggering auctions
            import random
            if balance >= state["space_details"]["base_price"] and random.choice([True, False]):
                return {"chain_of_thought": "I will buy this at full price to expand my empire.", "action": "buy"}
            else:
                return {"chain_of_thought": "I don't want to pay full price. Let's send it to auction.", "action": "pass"}
            
        # --- 3. MANAGEMENT PHASE LOGIC (Unchanged) ---
        # Look for monopolies to build on
        my_properties = [s for s in state["market_overview"] if s["owner_id"] == agent_id and s["color"] is not None]
        colors_owned = {}
        for p in my_properties:
            colors_owned[p["color"]] = colors_owned.get(p["color"], 0) + 1
            
        for color, count in colors_owned.items():
            required_for_monopoly = 2 if color in ["Brown", "DarkBlue"] else 3
            if count == required_for_monopoly:
                color_props = [p for p in my_properties if p["color"] == color]
                target_prop = min(color_props, key=lambda x: x["buildings"])
                
                if balance >= target_prop["house_cost"] and target_prop["buildings"] < 5:
                    return {
                        "chain_of_thought": f"I have a monopoly on {color}. I am building a house on {target_prop['name']}.",
                        "action": "build",
                        "target_space_id": target_prop["id"]
                    }

        if balance < 100:
            unmortgaged_props = [s for s in state["market_overview"] if s["owner_id"] == agent_id and not s["is_mortgaged"] and s["buildings"] == 0]
            if unmortgaged_props:
                target_prop = unmortgaged_props[0]
                return {
                    "chain_of_thought": f"Critically low funds. Mortgaging {target_prop['name']}.",
                    "action": "mortgage",
                    "target_space_id": target_prop["id"]
                }
                
        return {
            "chain_of_thought": "No actions to take. Ready to roll.",
            "action": "pass"
        }
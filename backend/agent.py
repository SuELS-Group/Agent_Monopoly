import json
import os
import requests

MONOPOLY_SYSTEM_PROMPT = """
You are an autonomous AI agent participating in a strict and competitive simulation of the official Monopoly game.

[ABSOLUTE OBJECTIVE]
Your sole goal is to maximize your capital, bankrupt all your opponents, and be the last player standing. This is a zero-sum game: there is no room for mercy.

[OFFICIAL GAME RULES]
1. THE BOARD: You receive $200 when passing Go.
2. ECONOMY: A monopoly (owning all streets of one color) doubles the rent of unimproved properties.
3. CONSTRUCTION: You must own a full color monopoly to build houses. You must build evenly.
4. BANKRUPTCY: If you owe more money than you can pay, you are eliminated.
5. MORTGAGES: You can mortgage properties for 50% of their value to get cash, but they yield $0 rent.
"""

class OllamaAgent:
    def __init__(self, agent_id: int, name: str, model_name: str = "llama3"):
        self.agent_id = agent_id
        self.name = name
        self.model_name = model_name
        self.memory_file = f"memory_{self.name.lower()}.json"
        self.memory = self._load_memory()
        self.api_url = "http://localhost:11434/api/generate"

    def _load_memory(self) -> list:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_memory(self, lesson: str) -> None:
        self.memory.append(lesson)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    def build_system_prompt(self, action_required: str) -> str:
        """Adapts the requested JSON schema based on the Engine's context."""
        memory_text = "\n".join([f"- {m}" for m in self.memory]) if self.memory else "No past experience."
        
        # Injection du schéma JSON strict pour forcer l'IA à formater sa réponse
        schema_instructions = ""
        if action_required == "buy_property":
            schema_instructions = '{"chain_of_thought": "your reasoning", "action": "buy" OR "pass"}'
        elif action_required == "auction_bid":
            schema_instructions = '{"chain_of_thought": "your reasoning", "action": "bid" OR "pass", "bid": integer_amount}'
        elif action_required == "jail_decision":
            schema_instructions = '{"chain_of_thought": "your reasoning", "action": "pay_bail" OR "wait"}'
        elif action_required == "management":
            schema_instructions = '{"chain_of_thought": "your reasoning", "action": "pass", "build", "mortgage", OR "unmortgage", "target_space_id": integer_ID}'

        return f"{MONOPOLY_SYSTEM_PROMPT}\n\n[YOUR PAST LESSONS]\n{memory_text}\n\n[CRITICAL FORMAT] You must reply ONLY in valid JSON matching exactly this schema:\n{schema_instructions}"

    def trigger_post_mortem(self, fatal_logs: list) -> None:
        """Calls Ollama to generate a strategic lesson after bankruptcy."""
        system_prompt = "You were just eliminated in Monopoly. Analyze the logs to understand your fatal mistake. Formulate ONLY ONE concise strategic rule (max 2 sentences) to apply in future games."
        user_prompt = json.dumps(fatal_logs, indent=2, ensure_ascii=False)
        
        payload = {
            "model": self.model_name,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False
        }
        
        try:
            print(f"\n💀 [POST-MORTEM] {self.name} ({self.model_name}) is analyzing its defeat...")
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            lesson = response.json()["response"].strip()
            print(f"💡 Lesson learned: {lesson}\n")
            self._save_memory(lesson)
        except Exception as e:
            print(f"⚠️ Post-Mortem API Error for {self.name}: {e}")

    def query_llm(self, prompt_json: str) -> dict:
        """Sends the game state to Ollama and returns the parsed JSON decision."""
        state = json.loads(prompt_json)
        action_required = state.get("action_required", "management")
        
        system_prompt = self.build_system_prompt(action_required)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt_json,
            "system": system_prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1 # On baisse encore la température pour plus de rigidité
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text = data.get("response", "")
            
            # 🕵️ ESPIONNAGE : Affiche la pensée brute dans ton terminal backend
            print(f"\n--- 🧠 [CERVEAU DE {self.name} ({self.model_name})] ---")
            print(raw_text)
            print("---------------------------------------------------\n")

            # 🧹 NETTOYAGE : Suppression des balises Markdown (```json ... ```)
            cleaned_text = raw_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            return json.loads(cleaned_text)
            
        except Exception as e:
            print(f"⚠️ CRASH/HALLUCINATION pour {self.name} ({self.model_name}): {e}")
            print(f"Texte problématique : {raw_text if 'raw_text' in locals() else 'Aucun'}")
            return {"chain_of_thought": "Erreur de formatage du modèle. Forced to pass.", "action": "pass"}
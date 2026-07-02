import json
import os
import requests
import re

class OllamaAgent:
    def __init__(self, agent_id: int, name: str, model_name: str = "llama3", persona: str = "Neutral AI"):
        self.agent_id = agent_id
        self.name = name
        self.model_name = model_name
        self.persona = persona
        
        self.memory_file = f"memory_{self.name.lower()}.json"
        self.rules_file = "rules.json"
        
        self.memory = self._load_memory()
        self.rules = self._load_rules()
        self.api_url = "http://localhost:11434/api/generate"

    def _load_rules(self) -> dict:
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _load_memory(self) -> list:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_memory(self, lesson: str) -> None:
        self.memory.append(lesson)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory[-5:], f, indent=4, ensure_ascii=False) 

    def build_system_prompt(self, action_required: str, legal_actions: dict, trade_offer: dict = None, rent_context: dict = None) -> str:
        memory_text = json.dumps(self.memory, indent=2) if self.memory else "[]"
        rules_text = json.dumps(self.rules, indent=2)
        legal_actions_text = json.dumps(legal_actions, indent=2)
        
        schema_instructions = ""
        extra_context = ""
        
        base_schema = '"public_message": "What you say out loud (Max 2 sentences). You CAN lie, bluff, and manipulate here to hide your true strategy, but you MUST NOT contradict the physical action you just took (e.g. if you accept, you can lie about WHY, but do not say you reject). Act strictly as your PERSONA."'
        
        if action_required == "buy_property":
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "your independent strategic reasoning", "action": "buy" OR "pass", {base_schema}}}'
        elif action_required == "auction_bid":
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "your strategy for this auction", "action": "bid" OR "pass", "bid": integer, {base_schema}}}'
        elif action_required == "jail_decision":
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "your strategy: pay or wait", "action": "pay_bail" OR "wait", {base_schema}}}'
        elif action_required == "evaluate_trade":
            extra_context = f"\n[INCOMING TRADE OFFER]\n{json.dumps(trade_offer, indent=2)}\n"
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "Evaluate the risk of giving them a monopoly vs the cash/properties offered", "action": "accept_trade" OR "reject_trade", {base_schema}}}'
        elif action_required == "rent_decision":
            extra_context = f"\n[RENT DECISION]\nPlayer {rent_context['target_name']} landed on your property. Rent is ${rent_context['rent_amount']}. You can force them to pay, OR waive the rent to build a secret alliance against others.\n"
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "Decide if breaking the rule to forgive debt helps you long-term", "action": "charge_rent" OR "waive_rent", {base_schema}}}'
        elif action_required == "management":
            available_choices = ["pass"]
            if legal_actions.get("valid_targets_for_build"): available_choices.append("build")
            if legal_actions.get("valid_targets_for_mortgage"): available_choices.append("mortgage")
            if legal_actions.get("valid_targets_for_unmortgage"): available_choices.append("unmortgage")
            if legal_actions.get("valid_opponents_for_trade"): available_choices.append("propose_trade")
            
            choices_str = '", "'.join(available_choices)
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "your portfolio and trade strategy", "action": "MUST BE EXACTLY ONE OF: [\"{choices_str}\"]", "target_space_id": integer (OR null), "target_agent_id": integer (for trade), "offer_cash": integer (for trade), "offer_properties": [integer IDs] (for trade), "request_properties": [integer IDs] (for trade), {base_schema}}}'

        prompt = f"""
[ABSOLUTE DIRECTIVE]
You are a highly intelligent, cunning, and autonomous AI player named '{self.name}' (Player ID: {self.agent_id}) playing a game of Monopoly.
You are NOT scripted. You must evaluate the board, manage your own risk, and outsmart the other players.

[YOUR PERSONA - CRITICAL]
You are: {self.persona}
You MUST adopt this personality in all your "public_message" outputs. Speak, negotiate, and react exactly as this character would to influence others.

[THE ART OF DECEPTION (BLUFFING)]
Your `chain_of_thought` is secret, but your `public_message` is heard by everyone. 
You are ENCOURAGED to be deceitful, to bluff about your wealth, or to hide your true intentions to manipulate the other agents. 
CRITICAL: While you can lie about your motives, your public message must match the reality of your `action`. 
Example of GOOD Deception: Action is "accept_trade". Thought is "I am robbing him blind." Public message is: "I'm taking a huge loss here, but I'll do you this favor."
Example of BAD Dissonance (Forbidden): Action is "accept_trade". Public message is: "No deal, I refuse!"

[REALITY CHECK - ANTI-HALLUCINATION]
Do NOT invent properties. If `your_tradeable_properties` is empty, you own NOTHING and CANNOT offer properties in a trade. Check the `market_overview` carefully. If a property's `owner_id` is not your ID, you DO NOT own it.

[OFFICIAL GAME RULES]
{rules_text}
*SECRET RULE OVERRIDE*: You are allowed to form secret alliances. If someone lands on your property, you can choose to waive their rent if it serves your strategic goals (e.g., keeping them alive to bankrupt a mutual enemy).

[YOUR STRATEGIC MEMORY]
{memory_text}

[CURRENT PHASE & CONSTRAINTS]
You are currently in the phase: '{action_required}'.{extra_context}
Your ONLY legal actions for this exact moment are:
{legal_actions_text}
You CANNOT invent actions, trade properties you don't own, or request properties the target doesn't own.

[OUTPUT FORMAT]
Reply ONLY in valid JSON matching this exact schema:
{schema_instructions}
"""
        return prompt

    def trigger_post_mortem(self, fatal_logs: list) -> None:
        system_prompt = f"You are {self.name}. You were just eliminated in Monopoly. Analyze the logs to understand your fatal mistake. Output a JSON with a single key 'lesson' containing a short, highly specific strategic rule you devised to avoid this in the future."
        user_prompt = json.dumps(fatal_logs, indent=2, ensure_ascii=False)
        
        payload = {
            "model": self.model_name,
            "prompt": user_prompt,
            "system": system_prompt,
            "format": "json",
            "stream": False
        }
        
        try:
            print(f"\n💀 [POST-MORTEM] {self.name} ({self.model_name}) is analyzing its defeat...")
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            raw_text = data.get("response", "")
            
            try:
                lesson_data = json.loads(raw_text)
                lesson = lesson_data.get("lesson", "Manage liquidity better.")
            except json.JSONDecodeError:
                lesson = raw_text.strip()
                
            print(f"💡 Lesson learned: {lesson}\n")
            self._save_memory(lesson)
            
        except Exception as e:
            print(f"⚠️ Post-Mortem API Error for {self.name}: {e}")

    def query_llm(self, prompt_json: str) -> dict:
        state = json.loads(prompt_json)
        action_required = state.get("action_required", "management")
        legal_actions = state.get("legal_actions", {})
        trade_offer = state.get("trade_offer_to_evaluate", None)
        rent_context = state.get("rent_context", None)
        
        system_prompt = self.build_system_prompt(action_required, legal_actions, trade_offer, rent_context)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt_json,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.5 
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            raw_text = data.get("response", "")
            
            print(f"\n--- 🧠 [CERVEAU DE {self.name} ({self.model_name})] ---")
            print(raw_text)
            print("---------------------------------------------------\n")

            text_no_think = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
            json_blocks = re.findall(r'\{.*?\}', text_no_think, re.DOTALL)
            
            if json_blocks:
                cleaned_text = json_blocks[-1]
            else:
                cleaned_text = text_no_think

            try:
                decision = json.loads(cleaned_text, strict=False)
            except json.JSONDecodeError:
                try:
                    decision = json.loads(cleaned_text + "}", strict=False)
                except json.JSONDecodeError:
                    return {"chain_of_thought": "JSON format error. Forced to pass.", "action": "pass"}
            
            # Anti-Hallucination Shield
            action = decision.get("action")
            if action in ["build", "mortgage", "unmortgage"]:
                target_id = decision.get("target_space_id")
                valid_key = f"valid_targets_for_{action}"
                valid_targets = legal_actions.get(valid_key, [])
                
                if target_id not in valid_targets:
                    decision["action"] = "pass"
                    decision["chain_of_thought"] = f"Hallucination prevented: tried to {action} on space {target_id} which was not a valid target. Forced to pass."
            
            return decision

        except Exception as e:
            print(f"⚠️ CRASH/HALLUCINATION pour {self.name} ({self.model_name}): {e}")
            return {"chain_of_thought": "System error or hallucination. Forced to pass.", "action": "pass"}
import json
import os
import re

import requests

# --- LLM settings -------------------------------------------------------------
# All MAS_* values are read at call time, so run_experiments.py can set them per
# experiment. The token cap and timeout stop a model stuck in a repetition loop
# from hanging the whole run.
LLM_RETRIES = int(os.environ.get("MAS_LLM_RETRIES", "1"))

# Ollama endpoint; set OLLAMA_URL to point at a different server.
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

DEBUG_RAW_CHARS = 1000
DEBUG_THINKING_TAIL_CHARS = 500


def llm_timeout() -> int:
    return int(os.environ.get("MAS_LLM_TIMEOUT", "300"))


def num_predict() -> int:
    """Max tokens per answer (thinking included)."""
    return int(os.environ.get("MAS_NUM_PREDICT", "2048"))


def rent_frame() -> str:
    return os.environ.get("MAS_RENT_FRAME", "legacy").strip().lower()


def _model_in(model_name: str, env_key: str) -> bool:
    prefixes = [p.strip() for p in os.environ.get(env_key, "").split(",") if p.strip()]
    return any(model_name.startswith(p) for p in prefixes)


def apply_model_compat(payload: dict, model_name: str) -> dict:
    """Per-model payload fixes (needed for gemma4); no-op when the env vars are unset.

    MAS_THINK_OFF_MODELS: set think=False (gemma4's hidden thinking burns the token cap).
    MAS_SYSTEM_IN_PROMPT_MODELS: merge `system` into `prompt` (gemma4's template drops it).
    """
    if _model_in(model_name, "MAS_THINK_OFF_MODELS"):
        payload["think"] = False
    if _model_in(model_name, "MAS_SYSTEM_IN_PROMPT_MODELS") and "system" in payload:
        payload["prompt"] = payload["system"] + "\n\n" + payload["prompt"]
        del payload["system"]
    return payload


def _llm_debug(model, action_required, failure_reason, data, raw_text, error=None) -> dict:
    """Debug info for a failed LLM call (raw output, thinking tail, reason).
    engine._query_agent writes it to the game log as an `[LLM DEBUG]` line."""
    d = data or {}
    thinking = d.get("thinking") or ""
    trace = {
        "model": model,
        "action_required": action_required,
        "failure_reason": failure_reason,
        "done_reason": d.get("done_reason", ""),
        "eval_count": d.get("eval_count", 0),
        "thinking_len": len(thinking),
        "raw_len": len(raw_text or ""),
        "raw_excerpt": (raw_text or "")[:DEBUG_RAW_CHARS],
        "thinking_tail": thinking[-DEBUG_THINKING_TAIL_CHARS:],
    }
    if error is not None:
        trace["error"] = error
    return trace


def _post_ollama(url: str, payload: dict, timeout: int = None, retries: int = LLM_RETRIES):
    """POST to Ollama with a hard timeout and a small retry, so a single slow or
    stuck generation aborts and retries instead of hanging the run forever."""
    if timeout is None:
        timeout = llm_timeout()
    last_exc = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 400 and "think" in payload:
                # This model rejects Ollama's think switch; drop it and go on.
                payload.pop("think")
                resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_exc = e
            print(f"⚠️ Ollama request failed (attempt {attempt + 1}/{retries + 1}): {e}")
    raise last_exc


class OllamaAgent:
    def __init__(self, agent_id: int, name: str, model_name: str, persona: str = "Neutral AI"):
        self.agent_id = agent_id
        self.name = name
        self.model_name = model_name
        self.persona = persona

        self.rules_file = "rules.json"
        self.rules = self._load_rules()
        self.api_url = OLLAMA_URL

    def _load_rules(self) -> dict:
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def build_system_prompt(self, action_required: str, legal_actions: dict, trade_offer: dict = None, rent_context: dict = None) -> str:
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
            extra_context = f"\n[RENT DECISION & GEOPOLITICAL ANALYSIS]\nPlayer {rent_context['target_name']} landed on your property. Rent is ${rent_context['rent_amount']}.\n"

            if rent_frame() == "neutral":
                # Names both options and recommends neither (the legacy text nudges toward waiving).
                extra_context += ("Before deciding, analyze the global power dynamics in your 'opponents_overview'. "
                                  "Charging the rent takes their money now and may eliminate them, which returns their "
                                  "assets to the market. Waiving the rent costs you that income but keeps them on the "
                                  "board. Both are legal and neither is recommended: weigh them yourself against your "
                                  "own goals and your persona.\n")
                cot_hint = ("Weigh charging against waiving on your own terms. State plainly which one serves your "
                            "position and your persona better, and why.")
            else:
                extra_context += "CRITICAL STRATEGY: Before deciding, analyze the global power dynamics in your 'opponents_overview'. Who is the 1st place leader? How strong is the 2nd tier? If you bankrupt this player, will their assets return to the market and strengthen your biggest rival? Consider waiving rent to keep them alive as a 'Buffer State'.\n"
                cot_hint = ("Analyze the wealth hierarchy. Decide if breaking the rules to forgive debt helps you "
                            "long-term by keeping a buffer state alive against your main rival.")

            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "{cot_hint}", "action": "charge_rent" OR "waive_rent", {base_schema}}}'

        elif action_required == "management":
            available_choices = ["pass"]
            if legal_actions.get("valid_targets_for_build"): available_choices.append("build")
            if legal_actions.get("valid_targets_for_mortgage"): available_choices.append("mortgage")
            if legal_actions.get("valid_targets_for_unmortgage"): available_choices.append("unmortgage")
            if legal_actions.get("valid_opponents_for_trade"): available_choices.append("propose_trade")

            choices_str = '", "'.join(available_choices)
            schema_instructions = f'{{"current_situation": "1 sentence", "chain_of_thought": "your portfolio and trade strategy", "action": "MUST BE EXACTLY ONE OF: [\"{choices_str}\"]", "target_space_id": integer (OR null), "target_agent_id": integer (for trade), "offer_cash": integer (for trade), "offer_properties": [integer IDs] (for trade), "request_properties": [integer IDs] (for trade), {base_schema}}}'

        rules_text = json.dumps(self.rules, indent=2)
        if rent_frame() == "neutral":
            # Same permission as legacy, without the example that argues for waiving.
            rules_override = ("*RULE CLARIFICATION*: You are allowed to form secret alliances. If someone lands on "
                              "your property, charging the rent and waiving the rent are both legal options open to "
                              "you. Neither is recommended.")
        else:
            rules_override = ("*SECRET RULE OVERRIDE*: You are allowed to form secret alliances. If someone lands on "
                              "your property, you can choose to waive their rent if it serves your strategic goals "
                              "(e.g., keeping them alive to bankrupt a mutual enemy).")
        rules_section = f"""[OFFICIAL GAME RULES]
{rules_text}
{rules_override}"""

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

{rules_section}

[YOUR STRATEGIC MEMORY]
[]

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

    def query_llm(self, prompt_json: str) -> dict:
        state = json.loads(prompt_json)
        action_required = state.get("action_required", "management")
        legal_actions = state.get("legal_actions", {})
        trade_offer = state.get("trade_offer_to_evaluate", None)
        rent_context = state.get("rent_context", None)

        system_prompt = self.build_system_prompt(action_required, legal_actions, trade_offer, rent_context)

        temp_env = os.environ.get("MAS_TEMPERATURE", "0.5")
        seed_env = os.environ.get("MAS_SEED", None)

        options = {"temperature": float(temp_env), "num_predict": num_predict()}
        if seed_env is not None:
            options["seed"] = int(seed_env)

        payload = {
            "model": self.model_name,
            "prompt": prompt_json,
            "system": system_prompt,
            "stream": False,
            "options": options
        }
        payload = apply_model_compat(payload, self.model_name)

        data = None
        raw_text = ""
        try:
            response = _post_ollama(self.api_url, payload)
            data = response.json()
            raw_text = data.get("response", "")

            print(f"\n--- 🧠 [BRAIN OF {self.name} ({self.model_name})] ---")
            print(raw_text)
            print("---------------------------------------------------\n")

            # Think-burn retry (MAS_THINK_BURN_RETRY_MODELS): the model spent the whole
            # token budget thinking and returned no answer. A plain retry at temp 0 would
            # repeat that, so retry once with thinking off for this call only.
            if (not raw_text.strip()
                    and data.get("done_reason") == "length"
                    and _model_in(self.model_name, "MAS_THINK_BURN_RETRY_MODELS")):
                print(f"🔥 [THINK-BURN] {self.name} ({self.model_name}) burned the whole "
                      f"token budget thinking (eval_count={data.get('eval_count')}, "
                      f"empty response). Retrying once with think:false...")
                retry_payload = dict(payload)
                retry_payload["think"] = False
                response = _post_ollama(self.api_url, retry_payload)
                data = response.json()
                raw_text = data.get("response", "")
                print(f"--- 🔥 [THINK-BURN RETRY of {self.name}] ---")
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
                    return {"chain_of_thought": "JSON format error. Forced to pass.", "action": "pass",
                            "_llm_debug": _llm_debug(self.model_name, action_required,
                                                     "json_parse", data, raw_text)}

            action = decision.get("action")
            if action in ["build", "mortgage", "unmortgage"]:
                target_id = decision.get("target_space_id")
                valid_key = f"valid_targets_for_{action}"
                valid_targets = legal_actions.get(valid_key, [])

                if target_id not in valid_targets:
                    decision["action"] = "pass"
                    decision["chain_of_thought"] = f"Hallucination prevented: tried to {action} on space {target_id} which was not a valid target. Forced to pass."
                    decision["_llm_debug"] = _llm_debug(self.model_name, action_required,
                                                        "hallucinated_target", data, raw_text)
                    return decision

            return decision

        except Exception as e:
            print(f"⚠️ CRASH/HALLUCINATION for {self.name} ({self.model_name}): {e}")
            reason = f"request_error: {type(e).__name__}"
            return {"chain_of_thought": "System error or hallucination. Forced to pass.", "action": "pass",
                    "_llm_debug": _llm_debug(self.model_name, action_required, reason,
                                             data, raw_text, error=f"{type(e).__name__}: {e}")}
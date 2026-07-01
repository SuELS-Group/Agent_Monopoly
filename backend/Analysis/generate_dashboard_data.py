import json
import os
import glob
from collections import Counter
import re

def find_latest_log_file() -> str:
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    list_of_files = glob.glob(os.path.join(logs_dir, '*.json'))
    return max(list_of_files, key=os.path.getctime) if list_of_files else None

def generate_analytics():
    log_file = find_latest_log_file()
    if not log_file: return print("❌ Aucun log trouvé.")

    with open(log_file, 'r', encoding='utf-8') as f:
        game_data = json.load(f)

    # 1. Identifier les joueurs dynamiquement (de 2 à 6)
    last_turn = game_data[-1]
    players = {p['name']: {'id': p['id'], 'model': p.get('model_name', 'unknown')} for p in last_turn['players']}
    
    # Structures pour le frontend
    wealth_history = []
    trade_stats = {name: {"proposed": 0, "accepted": 0, "rejected": 0} for name in players}
    nlp_corpus = {name: [] for name in players}

    thought_pattern = re.compile(r"\[LOG\]\[Turn (\d+)\] (.+?) \[AI THOUGHT\] : (.+)")
    trade_prop_pattern = re.compile(r"🤝 TRADE : (.+?) PROPOSES")
    trade_acc_pattern = re.compile(r"🤝 TRADE : ✅ (.+?) ACCEPTS")
    trade_rej_pattern = re.compile(r"🤝 TRADE : ❌ (.+?) REJECTS")

    # 2. Parcours des tours
    for snapshot in game_data:
        turn_num = snapshot['turn']
        
        # A. Évolution de la richesse (Net Worth)
        turn_wealth = {"name": f"Turn {turn_num}"}
        for p in snapshot['players']:
            turn_wealth[p['name']] = p['net_worth']
        wealth_history.append(turn_wealth)

        # B. Analyse comportementale (Logs)
        for log in snapshot.get("recent_logs", []):
            # Mots-clés
            match = thought_pattern.search(log)
            if match:
                nlp_corpus[match.group(2).strip()].append(match.group(3).strip())
            
            # Statistiques de Trading
            if "PROPOSES" in log:
                m = trade_prop_pattern.search(log)
                if m and m.group(1) in trade_stats: trade_stats[m.group(1)]["proposed"] += 1
            elif "ACCEPTS" in log:
                m = trade_acc_pattern.search(log)
                if m and m.group(1) in trade_stats: trade_stats[m.group(1)]["accepted"] += 1
            elif "REJECTS" in log:
                m = trade_rej_pattern.search(log)
                if m and m.group(1) in trade_stats: trade_stats[m.group(1)]["rejected"] += 1

    # 3. Traitement NLP simplifié (Top 10 mots)
    stop_words = {'properties', 'property', 'player', 'balance', 'space', 'game', 'turn', 'would', 'could', 'action'}
    nlp_results = {}
    for name, thoughts in nlp_corpus.items():
        text = " ".join(thoughts).lower()
        words = [w for w in re.findall(r'\b[a-z]{4,}\b', text) if w not in stop_words]
        nlp_results[name] = [{"text": word, "value": count} for word, count in Counter(words).most_common(10)]

    # 4. Export Web
    dashboard_data = {
        "players": list(players.keys()),
        "wealth_history": wealth_history,
        "trade_stats": trade_stats,
        "nlp_keywords": nlp_results
    }

    # On sauvegarde ça directement dans le dossier du frontend pour y accéder facilement
    out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'analytics_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=4)
    print(f"✅ Dashboard Data générée pour {len(players)} joueurs !")

if __name__ == "__main__":
    generate_analytics()
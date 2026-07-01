import json
import pandas as pd
import re
import os
import glob

def find_latest_log_file() -> str:
    # On remonte d'un dossier (..) pour aller chercher dans "logs"
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    list_of_files = glob.glob(os.path.join(logs_dir, '*.json'))
    
    if not list_of_files:
        raise FileNotFoundError(f"No JSON file found in the folder {logs_dir}")
        
    # Trouve le fichier le plus récemment créé
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def create_thematic_dataset(output_csv: str):
    try:
        json_filepath = find_latest_log_file()
        print(f"📁 File automatically detected:{os.path.basename(json_filepath)}")
    except FileNotFoundError as e:
        print(f"❌ Error : {e}")
        return

    print("⏳ Loading JSON file...")
    
    with open(json_filepath, 'r', encoding='utf-8') as f:
        game_data = json.load(f)

    extracted_thoughts = []
    
    # Regex pour capturer : Tour, Nom de l'Agent, et la Pensée
    thought_pattern = re.compile(r"\[LOG\]\[Turn (\d+)\] (.+?) \[AI THOUGHT\] : (.+)")

    print("🔍 Extraction of Chain of Thoughts...")
    for snapshot in game_data:
        logs = snapshot.get("recent_logs", [])
        
        for log in logs:
            match = thought_pattern.search(log)
            if match:
                turn = int(match.group(1))
                agent = match.group(2).strip()
                thought = match.group(3).strip()
                
                extracted_thoughts.append({
                    "Turn_Number": turn,
                    "Agent": agent,
                    "Chain_of_Thought": thought
                })

    if not extracted_thoughts:
        print("⚠️ No chain of thought found. Please check the format of your logs.")
        return

    # Conversion en DataFrame Pandas
    df = pd.DataFrame(extracted_thoughts)
    
    # Suppression des doublons
    initial_count = len(df)
    df = df.drop_duplicates(subset=["Turn_Number", "Agent", "Chain_of_Thought"])
    final_count = len(df)
    
    print(f"🧹 Cleaning : {initial_count - final_count} duplicates removed.")
    
    # Sauvegarde
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"✅ Extraction complete! Dataset generated : {output_csv} ({final_count} unique rows)")

if __name__ == "__main__":
    OUTPUT_FILE = "thematic_analysis_raw.csv"
    create_thematic_dataset(OUTPUT_FILE)
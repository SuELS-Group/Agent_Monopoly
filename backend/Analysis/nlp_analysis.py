import pandas as pd
import nltk
from nltk.corpus import stopwords
from collections import Counter
import re
import ssl

# Bypass SSL errors for NLTK downloads on some university networks
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Téléchargement silencieux des dicos NLTK
nltk.download('stopwords', quiet=True)

def extract_top_keywords(csv_filepath: str, top_n: int = 12):
    print(f"🧠 Launch of NLP analysis on {csv_filepath}...")
    
    try:
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"❌ File not found: {csv_filepath}")
        return

    # Configuration des Stopwords (mots à ignorer)
    stop_words = set(stopwords.words('english'))
    # On retire les mots parasites du jeu pour ne garder que la stratégie
    custom_stops = {'properties', 'property', 'player', 'balance', 'space', 'game', 'turn', 'would', 'could', 'action', 'avenue', 'rent', 'since', 'however', 'therefore'}
    stop_words.update(custom_stops)

    agents = df['Agent'].unique()
    
    for agent in agents:
        # Récupération de toutes les pensées de l'agent
        agent_thoughts = df[df['Agent'] == agent]['Chain_of_Thought'].dropna().astype(str).tolist()
        text = " ".join(agent_thoughts).lower()
        
        # Nettoyage et Tokenization (mots de 4 lettres minimum)
        words = re.findall(r'\b[a-z]{4,}\b', text)
        
        # Filtrage
        filtered_words = [w for w in words if w not in stop_words]
        
        # Comptage
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(top_n)
        
        # Affichage formaté pour le terminal
        print(f"\n🤖 Agent : {agent} (Based on {len(agent_thoughts)} key decisions)")
        print("-" * 45)
        for word, count in top_words:
            # Création d'une mini jauge visuelle
            bar = "█" * min(count, 20) 
            print(f"   🔸 {word.ljust(15)} : {str(count).ljust(3)} {bar}")
    
    print("\n✅ NLP analysis complete. These keywords can serve as a basis for the 'Themes'.")

if __name__ == "__main__":
    # Il va lire le fichier que l'on vient de générer
    INPUT_FILE = "thematic_analysis_raw.csv"
    extract_top_keywords(INPUT_FILE)
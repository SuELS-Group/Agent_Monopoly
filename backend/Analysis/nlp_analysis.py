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

# Silently download the NLTK dictionaries
nltk.download('stopwords', quiet=True)

def extract_top_keywords(csv_filepath: str, top_n: int = 12):
    print(f"🧠 Launch of NLP analysis on {csv_filepath}...")
    
    try:
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"❌ File not found: {csv_filepath}")
        return

    # Stopword configuration (words to ignore)
    stop_words = set(stopwords.words('english'))
    # Drop game-noise words so only the strategy vocabulary remains
    custom_stops = {'properties', 'property', 'player', 'balance', 'space', 'game', 'turn', 'would', 'could', 'action', 'avenue', 'rent', 'since', 'however', 'therefore'}
    stop_words.update(custom_stops)

    agents = df['Agent'].unique()
    
    for agent in agents:
        # Collect all of the agent's thoughts
        agent_thoughts = df[df['Agent'] == agent]['Chain_of_Thought'].dropna().astype(str).tolist()
        text = " ".join(agent_thoughts).lower()
        
        # Cleaning and tokenization (words of 4+ letters)
        words = re.findall(r'\b[a-z]{4,}\b', text)
        
        # Filtering
        filtered_words = [w for w in words if w not in stop_words]
        
        # Counting
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(top_n)
        
        # Formatted terminal output
        print(f"\n🤖 Agent : {agent} (Based on {len(agent_thoughts)} key decisions)")
        print("-" * 45)
        for word, count in top_words:
            # Build a small visual gauge
            bar = "█" * min(count, 20) 
            print(f"   🔸 {word.ljust(15)} : {str(count).ljust(3)} {bar}")
    
    print("\n✅ NLP analysis complete. These keywords can serve as a basis for the 'Themes'.")

if __name__ == "__main__":
    # Reads the file that extract_themes.py just generated
    INPUT_FILE = "thematic_analysis_raw.csv"
    extract_top_keywords(INPUT_FILE)
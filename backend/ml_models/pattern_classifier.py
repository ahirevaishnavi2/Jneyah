# ml_models/pattern_classifier.py
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hdbscan
from collections import Counter

class PatternClassifier:
    def __init__(self):
        # ===============================
        # LOAD DATASET
        # ===============================
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "cyber_text_patterns_dataset.csv")
        self.df = pd.read_csv(DATASET_PATH)
        print(f"✅ Loaded dataset from {DATASET_PATH}")

        # ===============================
        # DETECT TEXT COLUMN
        # ===============================
        possible_text_cols = ["message", "text", "content", "body", "sms", "email"]
        self.text_col = None
        for col in possible_text_cols:
            if col in self.df.columns:
                self.text_col = col
                break
        if self.text_col is None:
            raise ValueError(f"❌ No text column found. Columns: {list(self.df.columns)}")

        self.df[self.text_col] = self.df[self.text_col].astype(str)
        self.messages = self.df[self.text_col].tolist()
        print(f"✅ Using text column: '{self.text_col}'")
        print(f"✅ Loaded {len(self.messages)} messages")

        # ===============================
        # TF-IDF EMBEDDINGS
        # ===============================
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2), max_features=3000)
        self.X = self.vectorizer.fit_transform(self.messages)
        print("✅ TF-IDF embeddings created")

        # ===============================
        # HDBSCAN CLUSTERING
        # ===============================
        self.clusterer = hdbscan.HDBSCAN(min_cluster_size=3, metric="euclidean")
        self.labels = self.clusterer.fit_predict(self.X.toarray())
        self.df["cluster"] = self.labels
        print("✅ Clustering complete")
        print("Clusters found:", set(self.labels))

        # ===============================
        # CLUSTER NAMES
        # ===============================
        self.CLUSTER_NAMES = {
            -1: "Mixed High-Risk / Unknown",
            0: "Account & Banking Fraud",
            1: "Promotions / Neutral"
        }

        # ===============================
        # EMOTION KEYWORDS
        # ===============================
        self.EMOTION_KEYWORDS = {
            "fear": ["suspended", "blocked", "infected", "leaked", "compromised"],
            "urgency": ["urgent", "immediately", "now", "today", "act fast"],
            "authority": ["bank", "security", "government", "official"],
            "reward": ["won", "prize", "reward", "free", "cash"]
        }

    # ===============================
    # HELPER FUNCTIONS
    # ===============================
    def detect_emotions(self, text):
        found = []
        text = text.lower()
        for emotion, words in self.EMOTION_KEYWORDS.items():
            if any(w in text for w in words):
                found.append(emotion)
        return found

    def compute_risk(self, similarity, emotions, cluster_id):
        score = similarity * 60
        score += len(emotions) * 10
        if cluster_id == -1:
            score += 20
        return min(round(score, 2), 100)

    # ===============================
    # PREDICTION FUNCTION
    # ===============================
    def predict(self, text):
        vec = self.vectorizer.transform([text])
        sims = cosine_similarity(vec, self.X)[0]

        best_idx = np.argmax(sims)
        best_cluster = int(self.df.iloc[best_idx]["cluster"])
        similarity = sims[best_idx]

        emotions = self.detect_emotions(text)
        risk = self.compute_risk(similarity, emotions, best_cluster)

        return {
            "cluster": self.CLUSTER_NAMES.get(best_cluster, "Unknown"),
            "similarity": round(float(similarity), 3),
            "risk_score": risk,
            "detected_emotions": emotions
        }

    # Optional: return top keywords for a cluster
    def explain_cluster(self, cluster_id):
        cluster_id = int(cluster_id)
        texts = " ".join(self.df[self.df["cluster"] == cluster_id][self.text_col])
        words = texts.lower().split()
        return Counter(words).most_common(10)

import os
import re
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

class ScamClassifier:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "saved_models")
        os.makedirs(self.model_path, exist_ok=True)

        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
        )

        self.encoder = LabelEncoder()
        self.model = LogisticRegression(max_iter=1000, class_weight="balanced")

    def train(self, csv_file):
        df = pd.read_csv(csv_file)
        df = df[["text", "label"]].dropna()

        X = df["text"].astype(str)
        y = self.encoder.fit_transform(df["label"].astype(str))

        X_vec = self.vectorizer.fit_transform(X)
        self.model.fit(X_vec, y)

        preds = self.model.predict(X_vec)
        print(classification_report(y, preds))

        joblib.dump(self.model, f"{self.model_path}/scam_model.pkl")
        joblib.dump(self.vectorizer, f"{self.model_path}/scam_vectorizer.pkl")
        joblib.dump(self.encoder, f"{self.model_path}/scam_encoder.pkl")

    def predict(self, text):
        self.model = joblib.load(f"{self.model_path}/scam_model.pkl")
        self.vectorizer = joblib.load(f"{self.model_path}/scam_vectorizer.pkl")
        self.encoder = joblib.load(f"{self.model_path}/scam_encoder.pkl")

        vec = self.vectorizer.transform([text])
        pred = self.model.predict(vec)[0]
        prob = np.max(self.model.predict_proba(vec))

        return {
            "scam_type": self.encoder.inverse_transform([pred])[0],
            "confidence": round(prob * 100, 2),
        }
if __name__ == "__main__":
    clf = ScamClassifier()
    clf.train("../dataset/scam_dataset.csv")

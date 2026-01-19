import os
import re
import json
import joblib
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ML
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression

# NLP
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download required NLTK resources
for pkg in ["punkt", "stopwords", "wordnet"]:
    try:
        nltk.data.find(pkg)
    except:
        nltk.download(pkg)


# =========================
# TEXT PREPROCESSOR
# =========================
class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def clean(self, text):
        text = str(text).lower()
        text = re.sub(r"http\S+", " URL ", text)
        text = re.sub(r"\S+@\S+", " EMAIL ", text)
        text = re.sub(r"\d+", " NUM ", text)
        text = re.sub(r"[^\w\s]", " ", text)

        tokens = word_tokenize(text)
        tokens = [
            self.lemmatizer.lemmatize(w)
            for w in tokens
            if w not in self.stop_words and len(w) > 2
        ]
        return " ".join(tokens)


# =========================
# MAIN CLASSIFIER
# =========================
class AdvancedThreatClassifier:
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.dataset_path = os.path.join(self.base_path, "..", "dataset")
        self.model_path = os.path.join(self.base_path, "saved_models")
        os.makedirs(self.model_path, exist_ok=True)

        self.encoder = LabelEncoder()
        self.preprocessor = TextPreprocessor()

        self.vectorizer = TfidfVectorizer(
            max_features=6000,
            ngram_range=(1, 3),
            sublinear_tf=True,
        )

        self.model = None

    # =========================
    # LOAD & CLEAN DATA
    # =========================
    def load_dataset(self, filename):
        df = pd.read_csv(os.path.join(self.dataset_path, filename))

        # Keep only required columns
        df = df[["text", "label"]]

        # Drop missing values
        df = df.dropna(subset=["text", "label"])

        # Force label to string (CRITICAL FIX)
        df["label"] = df["label"].astype(str).str.strip()
        df["text"] = df["text"].astype(str)

        return df

    # =========================
    # TRAIN
    # =========================
    def train(self):
        print("\n🚀 Training Advanced Threat Classifier (REAL DATA)\n")

        train_df = self.load_dataset("cyber-threat-intelligence-splited_train.csv")
        val_df = self.load_dataset("cyber-threat-intelligence-splited_validate.csv")
        test_df = self.load_dataset("cyber-threat-intelligence-splited_test.csv")

        train_df = pd.concat([train_df, val_df], ignore_index=True)

        train_df["text"] = train_df["text"].apply(self.preprocessor.clean)
        test_df["text"] = test_df["text"].apply(self.preprocessor.clean)

        X_train = train_df["text"].values
        y_train = self.encoder.fit_transform(train_df["label"])

        X_test = test_df["text"].values
        y_test = self.encoder.transform(test_df["label"])

        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        lr = LogisticRegression(max_iter=1000, class_weight="balanced")
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=25,
            class_weight="balanced",
            n_jobs=-1,
        )

        self.model = VotingClassifier(
            estimators=[("lr", lr), ("rf", rf)],
            voting="soft",
        )

        self.model.fit(X_train_vec, y_train)

        preds = self.model.predict(X_test_vec)

        print("\n📊 Classification Report\n")
        print(
            classification_report(
                self.encoder.inverse_transform(y_test),
                self.encoder.inverse_transform(preds),
            )
        )

        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")

        print(f"✅ Accuracy: {acc:.4f}")
        print(f"✅ F1 Score: {f1:.4f}")

        # Save everything
        joblib.dump(self.model, os.path.join(self.model_path, "best_model.pkl"))
        joblib.dump(self.vectorizer, os.path.join(self.model_path, "vectorizer.pkl"))
        joblib.dump(self.encoder, os.path.join(self.model_path, "label_encoder.pkl"))

        with open(os.path.join(self.model_path, "metadata.json"), "w") as f:
            json.dump(
                {
                    "classes": self.encoder.classes_.tolist(),
                    "accuracy": acc,
                    "f1": f1,
                },
                f,
                indent=2,
            )

        print("\n💾 Model saved successfully")

    # =========================
    # LOAD MODEL
    # =========================
    def load(self):
        self.model = joblib.load(os.path.join(self.model_path, "best_model.pkl"))
        self.vectorizer = joblib.load(
            os.path.join(self.model_path, "vectorizer.pkl")
        )
        self.encoder = joblib.load(
            os.path.join(self.model_path, "label_encoder.pkl")
        )

    # =========================
    # PREDICT
    # =========================
    def predict(self, text):
        self.load()
        text = self.preprocessor.clean(text)
        vec = self.vectorizer.transform([text])
        pred = self.model.predict(vec)[0]
        prob = np.max(self.model.predict_proba(vec)) * 100

        return {
            "prediction": self.encoder.inverse_transform([pred])[0],
            "confidence": round(prob, 2),
        }


# =========================
# RUN
# =========================
if __name__ == "__main__":
    clf = AdvancedThreatClassifier()
    clf.train()

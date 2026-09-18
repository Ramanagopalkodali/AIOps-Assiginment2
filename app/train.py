from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


APP_DIR = Path(__file__).resolve().parent

DATA_PATH = APP_DIR / "spam_dataset.csv"
MODEL_PATH = APP_DIR / "model.joblib"


def train_model():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Run generate_dataset.py first."
        )

    # Load dataset
    df = pd.read_csv(DATA_PATH)
    X = df["text"]
    y = df["label"]

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(),
            ),
            (
                "classifier",
                MultinomialNB(),
            ),
        ]
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    return model


if __name__ == "__main__":
    model = train_model()

    print(f"Model saved to: {MODEL_PATH}")
    print("Training completed successfully.")
    
    test_messages = [
        "WIN a FREE laptop now! Click here: win-now.co/claim",
        "Can you send me the notes from basketball class?",
    ]

    predictions = model.predict(test_messages)

    print("\nSanity-check predictions:")

    for message, prediction in zip(test_messages, predictions):
        print(f"Message: {message}")
        print(f"Prediction: {prediction}")
        print()
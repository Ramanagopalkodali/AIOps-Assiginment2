import random
from pathlib import Path

import pandas as pd

SEED = 42
NUM_ROWS = 1000

OUTPUT_PATH = Path(__file__).resolve().parent / "spam_dataset.csv"



SPAM_TEMPLATES = [
    "WIN a FREE {prize} now! Click here: {url}",
    "Congratulations! You have WON a {prize}. Claim NOW at {url}",
    "URGENT: Your account will be suspended. Verify at {url}",
    "Limited time offer! Get {prize} FREE, click {url} today",
    "You've been selected for a {prize}! Reply YES to claim",
    "Cash prize alert: claim your {prize} before it expires! {url}",
]

HAM_TEMPLATES = [
    "Hey, are we still meeting for {activity} on {day}?",
    "Can you send me the notes from {activity} class?",
    "Don't forget about {activity} this {day}, see you there",
    "Thanks for helping with {activity} yesterday",
    "Running a bit late for {activity}, be there in 10 min",
    "What time does {activity} start on {day}?",
]

PRIZES = [
    "iPhone",
    "cash prize",
    "gift card",
    "vacation",
    "laptop",
]

URLS = [
    "bit.ly/xyz123",
    "tinyurl.com/abc",
    "win-now.co/claim",
]

ACTIVITIES = [
    "lunch",
    "the study group",
    "basketball",
    "the project meeting",
]

DAYS = [
    "Monday",
    "Friday",
    "tomorrow",
    "the weekend",
]


def generate_dataset():
    random.seed(SEED)

    rows = []

    for _ in range(NUM_ROWS):

        if random.random() < 0.3:
            template = random.choice(SPAM_TEMPLATES)

            message = template.format(
                prize=random.choice(PRIZES),
                url=random.choice(URLS),
            )

            rows.append((message, "spam"))

        else:
            template = random.choice(HAM_TEMPLATES)

            message = template.format(
                activity=random.choice(ACTIVITIES),
                day=random.choice(DAYS),
            )

            rows.append((message, "ham"))

    dataframe = pd.DataFrame(
        rows,
        columns=["text", "label"],
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return dataframe


if __name__ == "__main__":
    df = generate_dataset()

    print(f"Dataset generated: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")
    print("\nClass distribution:")
    print(df["label"].value_counts())

    print("\nFirst 5 rows:")
    print(df.head())
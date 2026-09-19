import csv
import random
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent / "shards"

random.seed(42)

ACTIVITIES = [
    "basketball",
    "database class",
    "machine learning class",
    "project meeting",
    "lab session",
]

DOMAINS = [
    "example.com",
    "university.edu",
    "mail.com",
]


def make_valid_email(index):
    return f"user{index}@{random.choice(DOMAINS)}"


def generate_shard(shard_index):
    rows = []

    total_rows = 20

    # Deterministic invalid-row counts:
    # 3, 4, 5, 3, 4, 5, 3, 4
    invalid_count = 3 + (shard_index % 3)

    invalid_positions = set(range(invalid_count))

    for row_index in range(total_rows):
        global_index = shard_index * total_rows + row_index

        name = f"User {global_index + 1}"
        email = make_valid_email(global_index + 1)
        activity = random.choice(ACTIVITIES)
        signup_source = "web"

        if row_index in invalid_positions:
            invalid_type = row_index % 3

            if invalid_type == 0:
                email = f"user{global_index + 1}@@invalid"
            elif invalid_type == 1:
                email = ""
            else:
                name = ""

        rows.append(
            {
                "user_id": global_index + 1,
                "name": name,
                "email": email,
                "activity": activity,
                "signup_source": signup_source,
            }
        )

    return rows, invalid_count


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating 8 signup shards...")

    expected_counts = []

    for shard_index in range(8):
        rows, invalid_count = generate_shard(shard_index)

        output_path = (
            OUTPUT_DIR / f"signup_shard_{shard_index}.csv"
        )

        with output_path.open("w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "user_id",
                    "name",
                    "email",
                    "activity",
                    "signup_source",
                ],
            )

            writer.writeheader()
            writer.writerows(rows)

        expected_counts.append(invalid_count)

        print(
            f"{output_path.name}: "
            f"{len(rows)} rows, "
            f"expected invalid={invalid_count}"
        )

    print()
    print("Expected invalid-row counts:")
    print(expected_counts)


if __name__ == "__main__":
    main()

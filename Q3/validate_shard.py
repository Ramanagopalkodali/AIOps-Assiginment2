import csv
import json
import os
import re
import time
from pathlib import Path

SHARD_DIR = Path(os.environ.get("SHARD_DIR", "/app/shards"))

completion_index = int(
    os.environ.get("JOB_COMPLETION_INDEX", "0")
)

pod_name = os.environ.get(
    "POD_NAME", "unknown"
)

node_name = os.environ.get(
    "NODE_NAME", "unknown"
)

shard_path = (
    SHARD_DIR /
    f"signup_shard_{completion_index}.csv"
)

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_row(row):
    required_fields = [
        "user_id",
        "name",
        "email",
    ]

    for field in required_fields:
        if not row.get(field, "").strip():
            return False

    email = row["email"].strip()

    if not EMAIL_PATTERN.match(email):
        return False

    return True


def main():

    if not shard_path.exists():
        raise FileNotFoundError(
            f"Shard not found: {shard_path}"
        )

    total_rows = 0
    invalid_rows = 0

    with shard_path.open(newline="") as f:

        reader = csv.DictReader(f)

        for row in reader:

            total_rows += 1

            if not validate_row(row):
                invalid_rows += 1

    # Small fixed delay so that the concurrent Pods
    # remain visible in kubectl output long enough
    # to demonstrate the requested parallelism.
    time.sleep(30)

    result = {
        "completion_index": completion_index,
        "shard": shard_path.name,
        "total_rows": total_rows,
        "invalid_rows": invalid_rows,
        "pod_name": pod_name,
        "node_name": node_name,
    }

    print(
        "RESULT_JSON:" +
        json.dumps(result, sort_keys=True)
    )


if __name__ == "__main__":
    main()

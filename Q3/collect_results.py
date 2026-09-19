import csv
import json
import re

from kubernetes import client, config


JOB_NAME = "signup-validation-job"
OUTPUT_FILE = "q3_results.csv"


def main():

    # Load the current kubectl configuration
    config.load_kube_config()

    v1 = client.CoreV1Api()

    # Find all Pods belonging to the Job
    pods = v1.list_namespaced_pod(
        namespace="default",
        label_selector=f"job-name={JOB_NAME}",
    )

    results = []

    pattern = re.compile(
        r"RESULT_JSON:(\{.*\})"
    )

    for pod in pods.items:

        pod_name = pod.metadata.name

        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace="default",
        )

        match = pattern.search(logs)

        if not match:
            print(
                f"WARNING: no RESULT_JSON found "
                f"in {pod_name}"
            )
            continue

        result = json.loads(match.group(1))

        results.append(result)

    # Sort by Indexed Job completion index
    results.sort(
        key=lambda x: x["completion_index"]
    )

    print()
    print("=== Q3 Validation Results ===")
    print()

    for result in results:

        print(
            f"Shard {result['completion_index']}: "
            f"invalid={result['invalid_rows']} / "
            f"{result['total_rows']} rows | "
            f"Pod={result['pod_name']} | "
            f"Node={result['node_name']}"
        )

    # Save results to CSV
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "completion_index",
                "shard",
                "total_rows",
                "invalid_rows",
                "pod_name",
                "node_name",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print(
        f"Saved {len(results)} results "
        f"to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()

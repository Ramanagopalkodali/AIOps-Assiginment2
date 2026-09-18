import time
import requests


URL = "http://localhost:8000/predict"

TEXT = "WIN a FREE laptop now! Click here: win-now.co/claim"

PAYLOAD = {
    "text": TEXT
}


def make_request():
    start = time.perf_counter()

    response = requests.post(
        URL,
        json=PAYLOAD,
        timeout=10,
    )

    elapsed = time.perf_counter() - start

    response.raise_for_status()

    return elapsed, response.json()


print("=== Redis Cache Benchmark ===")
print()

# First request: expected cache MISS
miss_time, miss_result = make_request()

print(f"First request  (cache miss): {miss_time * 1000:.3f} ms")
print(f"Result: {miss_result}")

# Second request: expected cache HIT
hit_time, hit_result = make_request()

print(f"Second request (cache hit):  {hit_time * 1000:.3f} ms")
print(f"Result: {hit_result}")

print()

if hit_time > 0:
    speedup = miss_time / hit_time
    reduction = ((miss_time - hit_time) / miss_time) * 100

    print(f"Speedup: {speedup:.2f}x")
    print(f"Latency reduction: {reduction:.2f}%")

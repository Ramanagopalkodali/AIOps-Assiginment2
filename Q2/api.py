import hashlib
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "model.joblib"
model = None
redis_client = None
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))


class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    label: str

#redis

def initialize_redis():
    """
    Redis is optional.

    Q1 and Q4 run without Redis.
    Q2 sets REDIS_HOST=cache and enables caching.
    """
    global redis_client

    if not REDIS_HOST:
        print("Redis caching disabled.")
        return

    try:
        import redis

        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
        )

        redis_client.ping()

        print(
            f"Redis connected: {REDIS_HOST}:{REDIS_PORT}"
        )

    except Exception as exc:
        redis_client = None

        print(
            f"Redis unavailable; continuing without cache: {exc}"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model not found: {MODEL_PATH}\n"
            "Run train.py before starting the API."
        )

    # Load model at application startup
    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    # Redis is optional for Q1/Q4 and enabled in Q2
    initialize_redis()

    yield


app = FastAPI(
    title="Spam Detection API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/healthz")
def healthz():
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )

    return {
        "status": "ok"
    }
    
    
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )

    text = request.text

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty",
        )


    cache_key = None

    if redis_client is not None:

        # Hash the exact input text to create a safe Redis key
        text_hash = hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

        cache_key = f"spam_prediction:{text_hash}"

        cached_value = redis_client.get(cache_key)

        if cached_value is not None:

            result = json.loads(cached_value)

            print(
                f"CACHE HIT: {text!r} -> {result['label']}"
            )
            return PredictionResponse(
                label=result["label"]
            )
        print(f"CACHE MISS: {text!r}")

    prediction = model.predict([text])[0]
    label = str(prediction)


    if redis_client is not None and cache_key is not None:
        cache_value = json.dumps(
            {
                "label": label
            }
        )
        redis_client.setex(
            cache_key,
            CACHE_TTL,
            cache_value,
        )
        print(
            f"CACHE STORE: {text!r} -> {label} "
            f"(TTL={CACHE_TTL}s)"
        )

    return PredictionResponse(
        label=label
    )
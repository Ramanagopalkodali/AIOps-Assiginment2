from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "model.joblib"

model = None


class PredictionRequest(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    label: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found: {MODEL_PATH}. Run train.py first.")
    model = joblib.load(MODEL_PATH)  # load once at startup
    print("Model loaded successfully.")
    yield


app = FastAPI(title="Spam Detection API", version="2.0.0", lifespan=lifespan)


@app.get("/healthz")
def healthz():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok","version": "2.0.0"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    return PredictionResponse(label=str(model.predict([request.text])[0]))


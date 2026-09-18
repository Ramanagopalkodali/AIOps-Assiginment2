# =========================
# Stage 1: Builder
# =========================
FROM python:3.12 AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt redis


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY Q2/api.py .
COPY app/model.joblib .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

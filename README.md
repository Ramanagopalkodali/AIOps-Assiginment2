# AIOps Module 3 — Infrastructure & Containerization

This repository contains the implementation for the AIOps Module 3 assignment:
Docker, Docker Compose, and Kubernetes.

## Repository Structure

```text
AIOps-Assiginment2/
│
├── app/
│   ├── api.py
│   ├── generate_dataset.py
│   ├── model.joblib
│   ├── spam_dataset.csv
│   └── train.py
│
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.naive
│
├── Q2/
│   ├── api.py
│   ├── benchmark_cache.py
│   ├── docker-compose.yml
│   └── Dockerfile
│
├── Q3/
│   ├── collect_results.py
│   ├── Dockerfile.job
│   ├── generate_shards.py
│   ├── indexed-job.yaml
│   ├── shards/
│   │   ├── signup_shard_0.csv
│   │   ├── signup_shard_1.csv
│   │   ├── signup_shard_2.csv
│   │   ├── signup_shard_3.csv
│   │   ├── signup_shard_4.csv
│   │   ├── signup_shard_5.csv
│   │   ├── signup_shard_6.csv
│   │   └── signup_shard_7.csv
│   └── validate_shard.py
│
├── Q4/
│   ├── api.py
│   ├── deployment.yaml
│   ├── Dockerfile
│   └── service.yaml
│
├── evidence/
│   ├── q1/
│   ├── q2/
│   ├── q3/
│   └── q4/
│
├── requirements.txt
├── README.md
└── report/
    └── aiops_module3_report.tex
```

## Directory Contents

### `app/`

Contains the original spam-detection application:

- `generate_dataset.py` — generates the synthetic spam/ham dataset.
- `spam_dataset.csv` — generated dataset.
- `train.py` — trains the TF-IDF + Naive Bayes model.
- `model.joblib` — trained model.
- `api.py` — FastAPI application.

### `docker/`

Contains the Docker implementations for Q1:

- `Dockerfile.naive` — single-stage Docker build.
- `Dockerfile` — multi-stage Docker build.

### `Q2/`

Contains the Redis caching implementation:

- `api.py` — spam API with Redis caching.
- `Dockerfile` — multi-stage API image.
- `docker-compose.yml` — API + Redis services.
- `benchmark_cache.py` — measures cache-miss and cache-hit latency.

### `Q3/`

Contains the Kubernetes Indexed Job implementation:

- `generate_shards.py` — generates the eight signup CSV shards.
- `shards/` — eight generated CSV input shards.
- `validate_shard.py` — validates one shard using `JOB_COMPLETION_INDEX`.
- `Dockerfile.job` — worker image.
- `indexed-job.yaml` — Kubernetes Indexed Job manifest.
- `collect_results.py` — collects worker results from Pod logs using the Kubernetes API.

### `Q4/`

Contains the Kubernetes Deployment implementation:

- `api.py` — API version used for the Deployment/rolling-update test.
- `Dockerfile` — API image.
- `deployment.yaml` — Kubernetes Deployment manifest.
- `service.yaml` — Kubernetes Service manifest.

### `evidence/`

Contains terminal outputs and experiment evidence for each question:

```text
evidence/q1/
evidence/q2/
evidence/q3/
evidence/q4/
```

### `report/`

Contains the LaTeX source for the final assignment report.

---

# Running the Project

## Requirements

- Docker
- Docker Compose
- Minikube
- kubectl
- Python 3.12
- Conda environment recommended

Activate the environment:

```bash
conda activate aiops
```

---

## Q1 — Docker Images

From the repository root:

```bash
docker build -t spam-api-naive:latest -f docker/Dockerfile.naive .
docker build -t spam-api-multistage:latest -f docker/Dockerfile .
```

Check the images:

```bash
docker images | grep spam-api
```

Run the multi-stage image:

```bash
docker run -d --name spam-api -p 8000:8000 spam-api-multistage:latest
```

Test:

```bash
curl http://localhost:8000/healthz
```

Prediction:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"WIN a FREE iPhone now!"}'
```

Stop and remove the container:

```bash
docker rm -f spam-api
```

---

## Q2 — Docker Compose + Redis

```bash
cd Q2
docker compose up -d --build
```

Check both services:

```bash
docker compose ps
```

Check the API:

```bash
curl http://localhost:8000/healthz
```

Check Redis:

```bash
docker compose exec redis redis-cli ping
```

Run the cache benchmark:

```bash
python benchmark_cache.py
```

Stop the stack:

```bash
docker compose down
```

---

## Q3 — Kubernetes Indexed Job

Start the two-node Minikube cluster:

```bash
minikube start \
  --nodes=2 \
  --cpus=2 \
  --memory=2048 \
  --driver=docker \
  --container-runtime=docker \
  --extra-config=kubelet.kube-reserved=cpu=2
```

Set the Docker container CPU limits used for the experiment:

```bash
docker update --cpus=2 minikube
docker update --cpus=2 minikube-m02
```

Verify allocatable CPU:

```bash
kubectl get nodes \
  -o custom-columns=NAME:.metadata.name,ALLOCATABLE:.status.allocatable.cpu
```

Generate the signup shards:

```bash
cd Q3
python generate_shards.py
```

Build the worker image into Minikube:

```bash
minikube image build --all \
  -t signup-validator:latest \
  -f Dockerfile.job .
```

Apply the Indexed Job:

```bash
kubectl apply -f indexed-job.yaml
```

Check the Job:

```bash
kubectl get job signup-validation-job
```

Check Pods and nodes:

```bash
kubectl get pods -o wide
```

Watch execution:

```bash
kubectl get pods -o wide -w
```

Collect the results through the Kubernetes API:

```bash
python collect_results.py
```

Check the collected results:

```bash
cat ../evidence/q3/q3_results.csv
```

Clean up the Job:

```bash
kubectl delete job signup-validation-job
```

---

## Q4 — Kubernetes Deployment

Apply the Deployment:

```bash
kubectl apply -f Q4/deployment.yaml
```

Apply the Service:

```bash
kubectl apply -f Q4/service.yaml
```

Check the Deployment and Pods:

```bash
kubectl get deployment spam-api
kubectl get pods -o wide
```

Check the Service:

```bash
kubectl get service spam-api-service
```

### Self-Healing

List the Pods:

```bash
kubectl get pods -l app=spam-api -o wide
```

Delete one Pod:

```bash
kubectl delete pod <pod-name>
```

Watch Kubernetes recreate it:

```bash
kubectl get pods -l app=spam-api -o wide -w
```

### Rolling Update

Update the Deployment image:

```bash
kubectl set image deployment/spam-api \
  spam-api=spam-api-multistage:v2
```

Check rollout status:

```bash
kubectl rollout status deployment/spam-api
```

Check rollout history:

```bash
kubectl rollout history deployment/spam-api
```

Check the updated API:

```bash
curl http://<service-address>/healthz
```

---

## Stop Minikube

When finished:

```bash
minikube stop
```

To completely remove the cluster:

```bash
minikube delete
```

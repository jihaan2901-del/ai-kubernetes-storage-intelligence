# AI Kubernetes Storage Intelligence

An **AI-driven Kubernetes storage monitoring and autoscaling system** that monitors container storage usage, predicts disk exhaustion time, and automatically scales database containers before storage runs out.

This project demonstrates **intelligent infrastructure management using Kubernetes, FastAPI, ML prediction, and a real-time dashboard.**

---

# Architecture

```
Load Generator
      │
      ▼
Mongo / Redis Pods
      │
      ▼
Storage Collector (kubectl + du)
      │
      ▼
SQLite Metrics Database
      │
      ▼
Prediction Engine
      │
      ▼
AI Autoscaler
      │
      ▼
Kubernetes Deployment Scaling
      │
      ▼
React Dashboard
```

The system continuously monitors storage usage inside containers and automatically scales the deployment when storage approaches a defined threshold.

---

# Key Features

* Real-time **storage monitoring for Kubernetes pods**
* **Machine learning prediction** for disk exhaustion
* **Automatic pod scaling** based on storage thresholds
* Smart load routing to **newly created pods**
* Real-time dashboard with graphs and metrics
* SQLite database for continuous training data collection

---

# Tech Stack

### Backend

* Python
* FastAPI
* SQLite
* scikit-learn
* kubectl subprocess monitoring

### Frontend

* React
* Recharts
* Vite

### Infrastructure

* Kubernetes / k3s
* Docker containers
* MongoDB
* Redis

---

# Project Structure

```
ai-kubernetes-storage-intelligence

backend
│
├── api.py
├── collector.py
├── db.py
├── predictor.py
├── scaler.py
├── scheduler.py
├── main.py
├── storage.db
│
├── loads
│   ├── mongo_load.py
│   └── redis_load.py
│
frontend
│
├── src
│   ├── App.jsx
│   ├── api.js
│   └── components
│
k8s
│
├── mongodb.yaml
├── redis.yaml
├── mongodb-service.yaml
└── redis-service.yaml
```

---

# How It Works

## 1 Storage Monitoring

The collector runs every few seconds and collects storage metrics from running pods.

Example command executed:

```
kubectl exec <pod> -- du -s /data/db
```

The result is converted to GB and stored in SQLite:

```
storage_metrics
---------------
timestamp
pod
storage_used
total_storage
```

---

## 2 Prediction Engine

The prediction engine estimates **time until disk full** using recent storage growth.

```
growth_rate = storage_change / time_change
time_to_full = remaining_storage / growth_rate
```

If storage growth continues, the system predicts how long before the pod reaches its storage limit.

---

## 3 AI Autoscaling

The autoscaler checks storage periodically.

Example rule:

```
if storage_used >= 8GB:
    scale deployment
```

Scaling command executed:

```
kubectl scale deployment mongodb --replicas=2
```

New pods are automatically created by Kubernetes.

---

## 4 Intelligent Load Routing

The load generator automatically sends traffic to the **newest pod**.

This ensures:

```
Pod1 fills → scale
Pod2 fills → scale
Pod3 fills → scale
```

instead of filling only the first container.

---

## 5 Dashboard

The React dashboard displays:

* total pods
* storage usage
* remaining storage
* prediction time
* real-time storage graphs
* pod health status

Dashboard auto refreshes every few seconds.

---

# Installation

## 1 Clone repository

```
git clone <repo-url>
cd ai-kubernetes-storage-intelligence
```

---

# Backend Setup

```
cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Start backend server:

```
python3 main.py
```

Backend runs on:

```
http://localhost:8000
```

---

# Frontend Setup

```
cd frontend

npm install
npm run dev
```

Open dashboard:

```
http://localhost:5173
```

---

# Kubernetes Setup

Deploy MongoDB and Redis:

```
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/redis.yaml
```

Create services:

```
kubectl apply -f k8s/mongodb-service.yaml
kubectl apply -f k8s/redis-service.yaml
```

Verify pods:

```
kubectl get pods
```

---

# Port Forward (for local testing)

```
kubectl port-forward svc/mongodb 30017:27017
kubectl port-forward svc/redis 30007:6379
```

---

# Load Generation

MongoDB load generator:

```
cd backend/loads
python3 mongo_load.py
```

Redis load generator:

```
python3 redis_load.py
```

These scripts continuously insert data to increase storage usage.

---

# Observing Autoscaling

Watch pods live:

```
kubectl get pods -w
```

When storage reaches the threshold:

```
⚡ Scaling mongodb → 2
```

New pods will appear.

---

# Monitoring Storage

Example command used internally:

```
kubectl exec <mongo-pod> -- du -sh /data/db
```

---

# Example System Flow

```
Mongo Pod 1
Storage: 8GB
Prediction: 5 minutes

AI Trigger → Scale

Mongo Pod 2 created

Load moves to Pod 2
```

---

# Useful Kubernetes Commands

Check pods

```
kubectl get pods
```

Watch scaling

```
kubectl get pods -w
```

Check services

```
kubectl get svc
```

Check endpoints

```
kubectl get endpoints
```

Check storage inside pod

```
kubectl exec <pod> -- du -sh /data/db
```

---

# Future Improvements

* predictive autoscaling based on ML forecasts
* Kubernetes operator implementation
* Grafana monitoring integration
* distributed load routing
* multi-node cluster support

---

# Demo Workflow

1 Start backend
2 Start frontend dashboard
3 Deploy Kubernetes containers
4 Start load generator
5 Storage increases
6 AI predicts disk exhaustion
7 Autoscaler triggers new pod
8 Dashboard updates in real time

---

# Author

Sai Kumar
AI Kubernetes Storage Intelligence Project

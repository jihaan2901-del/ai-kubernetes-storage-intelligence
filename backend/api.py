from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sqlite3
import pandas as pd
from scaler import recommendation
from predictor import predict_full_time
from db import get_state, set_state
from scaler import scale_down


DB_FILE = "storage.db"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except:
        return None


def get_running_pods():

    try:
        out = subprocess.check_output(
            "kubectl get pods -o jsonpath='{.items[*].metadata.name}'",
            shell=True
        ).decode().replace("'", "")

        return out.split()

    except:
        return []


@app.get("/pods")
def get_pods():

    running_pods = get_running_pods()

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("SELECT * FROM storage_metrics", conn)

    conn.close()

    pods = []

    for pod in df["pod"].unique():

        if pod not in running_pods:
            continue

        pod_df = df[df["pod"] == pod]

        latest = pod_df.iloc[-1]

        used = float(latest["storage_used"])
        total = float(latest["total_storage"])

        state = get_state(pod)

        pods.append({
            "name": pod,
            "label": pod.split("-")[0],
            "state": state,
            "used": used,
            "total": total,
            "remaining": total - used,
            "prediction": predict_full_time(pod),
            "history": pod_df[
                ["timestamp", "storage_used"]
            ].to_dict(orient="records")
        })

    return {"pods": pods}


@app.post("/stop/{pod}")
def stop_pod(pod: str):

    set_state(pod, "INACTIVE")

    return {
        "status": "inactive",
        "pod": pod
    }


@app.post("/delete/{pod}")
def delete_pod(pod: str):

    replicas = run_cmd(
        "kubectl get deployment mongodb -o jsonpath='{.spec.replicas}'"
    )

    replicas = int(replicas.replace("'", ""))

    if replicas > 1:

        new_replicas = replicas - 1

        run_cmd(f"kubectl scale deployment mongodb --replicas={new_replicas}")

    return {
        "status": "scaled_down",
        "replicas": replicas - 1
    }
    
@app.post("/start/{pod}")
def start_pod(pod: str):

    from db import set_state

    set_state(pod, "ACTIVE")

    return {
        "status": "started",
        "pod": pod
    }

@app.get("/recommendation")
def get_recommendation():

    return {
        "scale_down_recommended": recommendation
    }

@app.post("/scale-down")
def manual_scale_down():

    scale_down()

    return {"status": "scaled_down"}
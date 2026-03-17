from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sqlite3
import pandas as pd
from scaler import get_recommendation
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

def get_node_storage():

    out = run_cmd("df -BG / | awk 'NR==2 {print $2,$3}'")

    if not out:
        return {"total":113,"used":0}

    total, used = out.split()

    total = int(total.replace("G",""))
    used = int(used.replace("G",""))

    return {
        "total": total,
        "node_used": used
    }


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
    
@app.post("/start/{pod}")
def start_pod(pod: str):

    from db import set_state

    set_state(pod, "ACTIVE")

    return {
        "status": "started",
        "pod": pod
    }

@app.get("/recommendation")
def get_recommendation_api():

    replicas = run_cmd(
        "kubectl get deployment mongodb -o jsonpath='{.spec.replicas}'"
    )

    replicas = int(replicas.replace("'", ""))

    return {
        "scale_down_recommended": get_recommendation() and replicas > 1
    }

@app.post("/scale-down")
def manual_scale_down():

    scale_down()

    return {"status": "scaled_down"}

@app.get("/cluster-storage")
def cluster_storage():

    # get running pods
    pods_cmd = "kubectl get pods --field-selector=status.phase=Running -o jsonpath='{.items[*].metadata.name}'"
    pods_raw = run_cmd(pods_cmd)

    pods = []

    if pods_raw:
        pods = pods_raw.replace("'", "").split()

    total_used = 0

    for pod in pods:

        # check redis path
        redis = run_cmd(f"kubectl exec {pod} -- sh -c 'du -sk /data 2>/dev/null'")
        
        # check mongodb path
        mongo = run_cmd(f"kubectl exec {pod} -- sh -c 'du -sk /data/db 2>/dev/null'")

        out = redis if redis else mongo

        if out:
            kb = int(out.split()[0])
            gb = kb / (1024 * 1024)
            total_used += gb

    # get total node storage
    raw = run_cmd(
        "kubectl get node -o jsonpath='{.items[0].status.capacity.ephemeral-storage}'"
    )

    raw = raw.replace("'", "")

    total_gb = 0

    if "Ki" in raw:
        total_gb = int(raw.replace("Ki","")) / (1024 * 1024)

    elif "Mi" in raw:
        total_gb = int(raw.replace("Mi","")) / 1024

    elif "Gi" in raw:
        total_gb = int(raw.replace("Gi",""))

    return {
        "containers_used": round(total_used,2),
        "cluster_total": round(total_gb,2)
    }
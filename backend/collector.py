import subprocess
import pandas as pd
import time
import os

FILE_PATH = "data/storage.csv"


def run_cmd(cmd):
    """Run shell command and return output"""
    try:
        out = subprocess.check_output(cmd, shell=True).decode().strip()
        return out
    except subprocess.CalledProcessError as e:
        print("Command failed:", cmd)
        print(e)
        return None


def get_pod(label):
    """Get pod name by label"""
    cmd = f"kubectl get pods -l app={label} -o jsonpath='{{.items[0].metadata.name}}'"
    pod = run_cmd(cmd)

    if not pod:
        print(f"No pod found for {label}")
        return None

    return pod


def get_storage(pod, path):
    """Get folder size inside container"""
    cmd = f"kubectl exec {pod} -- sh -c 'du -s {path} 2>/dev/null'"
    out = run_cmd(cmd)

    if not out:
        return 0

    size_kb = int(out.split()[0])
    size_gb = size_kb / (1024 * 1024)

    return size_gb


def collect_data():

    redis_pod = get_pod("redis")
    mongo_pod = get_pod("mongodb")

    records = []

    if redis_pod:
        redis_storage = get_storage(redis_pod, "/data")

        records.append({
            "timestamp": time.time(),
            "pod": "redis",
            "storage_used": redis_storage,
            "total_storage": 10
        })

    if mongo_pod:
        mongo_storage = get_storage(mongo_pod, "/data/db")

        records.append({
            "timestamp": time.time(),
            "pod": "mongodb",
            "storage_used": mongo_storage,
            "total_storage": 10
        })

    if not records:
        print("No storage data collected")
        return

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame(records)

    if not os.path.exists(FILE_PATH):
        df.to_csv(FILE_PATH, index=False)
    else:
        df.to_csv(FILE_PATH, mode="a", header=False, index=False)

    print("Collected storage:", records)
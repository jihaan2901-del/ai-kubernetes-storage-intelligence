import subprocess
import time
from db import insert_metric


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except:
        return None


def get_pods(label):

    cmd = f"kubectl get pods -l app={label} --field-selector=status.phase=Running -o jsonpath='{{.items[*].metadata.name}}'"
    out = run_cmd(cmd)

    if not out:
        return []

    return out.split()


def get_storage(pod, path):
    cmd = f"kubectl exec {pod} -- sh -c 'du -s {path} 2>/dev/null'"
    out = run_cmd(cmd)

    if not out:
        return 0

    kb = int(out.split()[0])
    return kb / (1024 * 1024)


def collect_data():

    now = time.time()

    redis_pods = get_pods("redis")
    mongo_pods = get_pods("mongodb")

    for pod in redis_pods:
        used = get_storage(pod, "/data")
        insert_metric(now, pod, used, 10)

    for pod in mongo_pods:
        used = get_storage(pod, "/data/db")
        insert_metric(now, pod, used, 10)
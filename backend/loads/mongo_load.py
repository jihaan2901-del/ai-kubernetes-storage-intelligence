import subprocess
import pymongo
import random
import string
import time
import sqlite3

DB = "../storage.db"


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except:
        return ""


def get_active_mongo_pods():

    # get states from DB
    conn = sqlite3.connect(DB)

    states = dict(conn.execute(
        "SELECT pod,state FROM pod_state"
    ).fetchall())

    conn.close()

    # get running mongo pods
    cmd = """kubectl get pods -l app=mongodb \
    --field-selector=status.phase=Running \
    -o jsonpath='{range .items[*]}{.metadata.name} {.status.podIP} {.metadata.creationTimestamp}{"\\n"}{end}'"""

    out = run_cmd(cmd).replace("'", "")

    pods = []

    for line in out.strip().split("\n"):

        parts = line.split()

        # skip incomplete lines
        if len(parts) < 3:
            continue

        name, ip, ts = parts

        # skip inactive pods
        if states.get(name, "ACTIVE") != "ACTIVE":
            continue

        pods.append((name, ip, ts))

    if not pods:
        return None

    # choose newest pod
    pods.sort(key=lambda x: x[2])

    return pods[-1]


print("🔥 Mongo Load Generator Started")


current_pod = None
client = None
collection = None


while True:

    pod = get_active_mongo_pods()

    if not pod:
        time.sleep(1)
        continue

    pod_name, pod_ip, _ = pod

    # reconnect if new pod
    if current_pod != pod_name:

        try:

            client = pymongo.MongoClient(
                f"mongodb://{pod_ip}:27017",
                serverSelectionTimeoutMS=2000
            )

            db = client["loadtest"]
            collection = db["data"]

            current_pod = pod_name

            print(f"🔌 Connected → {pod_name}")

        except:
            print("Mongo not ready yet...")
            time.sleep(1)
            continue

    try:

        docs = []

        # batch insert for speed
        for _ in range(100):

            text = "".join(random.choices(string.ascii_letters, k=200000))

            docs.append({"data": text})

        collection.insert_many(docs)

        print(f"Inserted batch → {pod_name}")

    except Exception as e:

        print("⚠ Mongo connection lost, retrying...")

        current_pod = None

        time.sleep(1)

    time.sleep(0.02)
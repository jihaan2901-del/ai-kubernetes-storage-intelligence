import subprocess
import pymongo


def get_newest_mongo():

    cmd = "kubectl get pods -l app=mongodb -o jsonpath='{range .items[*]}{.metadata.name} {.status.podIP} {.metadata.creationTimestamp}{\"\\n\"}{end}'"

    out = subprocess.check_output(cmd, shell=True).decode().replace("'", "")

    pods = []

    for line in out.strip().split("\n"):
        name, ip, ts = line.split()
        pods.append((name, ip, ts))

    pods.sort(key=lambda x: x[2])

    return pods[-1]


name, ip, _ = get_newest_mongo()

client = pymongo.MongoClient(f"mongodb://{ip}:27017")

db = client["loadtest"]

db.drop_collection("data")

print(f"🔥 Cleared Mongo pod → {name}")
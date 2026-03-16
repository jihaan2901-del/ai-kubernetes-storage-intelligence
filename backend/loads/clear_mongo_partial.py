import subprocess
import pymongo
import sys

if len(sys.argv) < 2:
    print("Usage: python3 clear_mongo_partial.py <pod-name>")
    exit()

pod = sys.argv[1]


def get_pod_ip(name):

    cmd = f"kubectl get pod {name} -o jsonpath='{{.status.podIP}}'"
    ip = subprocess.check_output(cmd, shell=True).decode().replace("'", "")

    return ip


def get_storage(name):

    cmd = f"kubectl exec {name} -- du -s /data/db"
    out = subprocess.check_output(cmd, shell=True).decode()

    kb = int(out.split()[0])

    return kb / (1024 * 1024)


ip = get_pod_ip(pod)

client = pymongo.MongoClient(f"mongodb://{ip}:27017")

db = client["loadtest"]
collection = db["data"]

print("Deleting documents...")

docs = collection.find().limit(50000)

ids = [d["_id"] for d in docs]

collection.delete_many({"_id": {"$in": ids}})

print("Running compact to free disk...")

subprocess.run(
    f"kubectl exec {pod} -- mongosh --eval 'db.runCommand({{compact:\"data\"}})' loadtest",
    shell=True
)

size = get_storage(pod)

print("Storage now:", round(size,2), "GB")
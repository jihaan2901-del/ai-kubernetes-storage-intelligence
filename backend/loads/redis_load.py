import subprocess
import redis
import random
import string
import time


def get_newest_redis_pod():

    cmd = "kubectl get pods -l app=redis -o jsonpath='{range .items[*]}{.metadata.name} {.status.podIP} {.metadata.creationTimestamp}{\"\\n\"}{end}'"

    out = subprocess.check_output(cmd, shell=True).decode().replace("'", "")

    pods = []

    for line in out.strip().split("\n"):
        name, ip, ts = line.split()
        pods.append((name, ip, ts))

    pods.sort(key=lambda x: x[2])

    return pods[-1]


print("🔥 Redis Load Generator Started")

while True:

    pod_name, pod_ip, _ = get_newest_redis_pod()

    r = redis.Redis(host=pod_ip, port=6379, decode_responses=True)

    key = ''.join(random.choices(string.ascii_letters, k=10))
    value = ''.join(random.choices(string.ascii_letters, k=200000))

    r.set(key, value)

    print(f"Inserted → {pod_name}")

    time.sleep(0.05)
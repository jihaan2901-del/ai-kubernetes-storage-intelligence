import subprocess
import redis


def get_newest_redis():

    cmd = "kubectl get pods -l app=redis -o jsonpath='{range .items[*]}{.metadata.name} {.status.podIP} {.metadata.creationTimestamp}{\"\\n\"}{end}'"

    out = subprocess.check_output(cmd, shell=True).decode().replace("'", "")

    pods = []

    for line in out.strip().split("\n"):
        name, ip, ts = line.split()
        pods.append((name, ip, ts))

    pods.sort(key=lambda x: x[2])

    return pods[-1]


name, ip, _ = get_newest_redis()

r = redis.Redis(host=ip, port=6379)

r.flushall()

print(f"🔥 Cleared Redis pod → {name}")
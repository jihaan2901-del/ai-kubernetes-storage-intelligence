import sqlite3
import subprocess
import time

DB = "storage.db"

THRESHOLD = 8
OBSERVE_THRESHOLD = 5

MAX_REPLICAS = 5
MIN_REPLICAS = 1

COOLDOWN = 60

last_scale_time = 0
scaled_recently = False

observation_start = None
initial_storage = None
recommendation = False


def run(cmd):
    try:
        print("Running:", cmd)
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except Exception as e:
        print("Command failed:", e)
        return None


# ----------------------------
# Find newest Mongo pod
# ----------------------------
def get_newest_pod():

    cmd = """
    kubectl get pods -l app=mongodb \
    -o jsonpath='{range .items[*]}{.metadata.name} {.metadata.creationTimestamp}{"\\n"}{end}'
    """

    out = run(cmd)

    if not out:
        return None

    out = out.replace("'", "")

    pods = []

    for line in out.strip().split("\n"):

        parts = line.split()

        if len(parts) < 2:
            continue

        name, ts = parts
        pods.append((name, ts))

    if not pods:
        return None

    pods.sort(key=lambda x: x[1])

    newest = pods[-1][0]

    print("Newest Mongo Pod:", newest)

    return newest


# ----------------------------
# Get replica count
# ----------------------------
def get_replicas():

    out = run("kubectl get deployment mongodb -o jsonpath='{.spec.replicas}'")

    if not out:
        return 1

    return int(out.replace("'", ""))


# ----------------------------
# Scale UP
# ----------------------------
def scale_up():

    global last_scale_time
    global scaled_recently

    replicas = get_replicas()

    print("Current replicas:", replicas)

    if replicas >= MAX_REPLICAS:
        print("Max replicas reached")
        return

    new_replicas = replicas + 1

    print("⚡ Scaling UP mongodb →", new_replicas)

    run(f"kubectl scale deployment mongodb --replicas={new_replicas}")

    last_scale_time = time.time()
    scaled_recently = True


# ----------------------------
# Scale DOWN
# ----------------------------
def scale_down():

    global last_scale_time
    global recommendation

    replicas = get_replicas()

    if replicas <= MIN_REPLICAS:
        print("Min replicas reached")
        return

    new_replicas = replicas - 1

    print("⬇ Scaling DOWN mongodb →", new_replicas)

    run(f"kubectl scale deployment mongodb --replicas={new_replicas}")

    last_scale_time = time.time()
    recommendation = False


# ----------------------------
# Main autoscaling logic
# ----------------------------
def check_and_scale():

    global scaled_recently
    global observation_start
    global initial_storage
    global recommendation

    now = time.time()

    newest_pod = get_newest_pod()

    if not newest_pod:
        return

    conn = sqlite3.connect(DB)

    row = conn.execute("""
        SELECT storage_used
        FROM storage_metrics
        WHERE pod = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (newest_pod,)).fetchone()

    conn.close()

    if not row:
        print("No storage metrics yet")
        return

    used = row[0]

    print("Storage for newest pod:", newest_pod, "→", used)

    # cooldown protection
    if now - last_scale_time < COOLDOWN:
        print("Cooldown active")
        return

    # ----------------------------
    # SCALE UP
    # ----------------------------
    if used >= THRESHOLD and not scaled_recently:

        scale_up()

        print("Scaling triggered")

        return

    # reset lock when load shifts
    if used < OBSERVE_THRESHOLD:
        scaled_recently = False

    # ----------------------------
    # SCALE DOWN OBSERVATION
    # ----------------------------
    if used <= OBSERVE_THRESHOLD:

        if observation_start is None:

            observation_start = now
            initial_storage = used

            print("Starting scale-down observation")

        else:

            elapsed = now - observation_start

            print("Observation time:", int(elapsed), "seconds")

            if elapsed >= 300:

                if abs(used - initial_storage) < 0.2:

                    recommendation = True

                    print("⚠ Downscale recommended")

    else:

        observation_start = None
        initial_storage = None
        recommendation = False


# ----------------------------
# API helper
# ----------------------------
def get_recommendation():

    return recommendation
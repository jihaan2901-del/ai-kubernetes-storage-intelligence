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


# ----------------------------
# Run shell command
# ----------------------------
def run(cmd):
    try:
        print("Running command:", cmd)
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
        print("No Mongo pods found")
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
        print("No valid Mongo pod entries")
        return None

    pods.sort(key=lambda x: x[1])

    newest = pods[-1][0]

    print("🧠 Newest Mongo Pod:", newest)

    return newest


# ----------------------------
# Get replica count
# ----------------------------
def get_replicas():

    out = run("kubectl get deployment mongodb -o jsonpath='{.spec.replicas}'")

    if not out:
        return 1

    replicas = int(out.replace("'", ""))

    print("Current Mongo replicas:", replicas)

    return replicas


# ----------------------------
# Scale UP
# ----------------------------
def scale_up():

    global last_scale_time
    global scaled_recently
    global observation_start
    global initial_storage

    replicas = get_replicas()

    if replicas >= MAX_REPLICAS:
        print("⚠ Max replicas reached")
        return

    new_replicas = replicas + 1

    print("🚀 Scaling UP MongoDB →", new_replicas)

    run(f"kubectl scale deployment mongodb --replicas={new_replicas}")

    last_scale_time = time.time()

    scaled_recently = True

    observation_start = None
    initial_storage = None

    print("Scale-up complete. Observation window reset.")


# ----------------------------
# Scale DOWN
# ----------------------------
def scale_down():

    global recommendation
    global observation_start
    global initial_storage

    replicas = get_replicas()

    print("Current replicas:", replicas)

    if replicas <= MIN_REPLICAS:

        print("⚠ Cannot scale below minimum replicas")
        recommendation = False
        return

    new_replicas = replicas - 1

    print("⬇ Scaling DOWN MongoDB →", new_replicas)

    run(f"kubectl scale deployment mongodb --replicas={new_replicas}")

    recommendation = False

    observation_start = None
    initial_storage = None
    print("scale down completed..")


# ----------------------------
# Main autoscaling logic
# ----------------------------
def check_and_scale():

    global observation_start
    global initial_storage
    global recommendation

    now = time.time()

    print("\n---------------- AUTOSCALER CHECK ----------------")

    newest_pod = get_newest_pod()

    if not newest_pod:
        print("No Mongo pod detected")
        return

    replicas = get_replicas()

    print("Mongo replica count:", replicas)

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

    # ----------------
    # SCALE UP
    # ----------------
    if used >= THRESHOLD and replicas < MAX_REPLICAS:

        print("🚨 Threshold exceeded → scaling up")

        scale_up()

        return


    # ----------------
    # SCALE DOWN OBSERVATION
    # ----------------
    if replicas > 1 and used <= OBSERVE_THRESHOLD:

        print("Observation condition satisfied (replicas > 1 and storage <= threshold)")

        if observation_start is None:

            observation_start = now
            initial_storage = used

            print("👀 Starting 5-minute observation window")
            print("Initial storage:", initial_storage)

        else:

            elapsed = now - observation_start

            print("⏱ Observation running:", int(elapsed), "seconds")

            if elapsed >= 300:

                change = abs(used - initial_storage)

                print("Storage change:", change)

                if change < 0.2:

                    recommendation = True

                    print("⚠ Downscale recommended")

                else:

                    print("Storage unstable → resetting observation")

                    observation_start = None

    else:

        if observation_start is not None:

            print("❌ Observation reset")

        observation_start = None
        initial_storage = None
        recommendation = False

# ----------------------------
# API helper
# ----------------------------
def get_recommendation():

    print("Recommendation status:", recommendation)

    return recommendation
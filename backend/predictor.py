import sqlite3
import pandas as pd

DB_FILE = "storage.db"
LIMIT = 10  # GB


def predict_full_time(pod):

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query(
        "SELECT * FROM storage_metrics WHERE pod=? ORDER BY timestamp",
        conn,
        params=(pod,)
    )

    conn.close()

    if len(df) < 6:
        return "Collecting data..."

    # use last 6 records only
    df = df.tail(6)

    first = df.iloc[0]
    last = df.iloc[-1]

    time_diff = last["timestamp"] - first["timestamp"]
    storage_diff = last["storage_used"] - first["storage_used"]

    if time_diff <= 0 or storage_diff <= 0:
        return "No growth"

    growth_rate = storage_diff / time_diff  # GB per second

    remaining = LIMIT - last["storage_used"]

    if remaining <= 0:
        return "Disk Full"

    seconds = remaining / growth_rate

    # prevent unrealistic predictions
    if seconds < 60:
        return "< 1 minute"

    minutes = seconds / 60
    hours = minutes / 60

    return f"{round(minutes,2)} minutes (~{round(hours,2)} hours)"
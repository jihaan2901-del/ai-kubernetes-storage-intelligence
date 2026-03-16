import sqlite3

DB_FILE = "storage.db"


# ------------------------------------------------
# Database initialization
# ------------------------------------------------

def init_db():

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()

    # storage metrics table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS storage_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        pod TEXT,
        storage_used REAL,
        total_storage REAL
    )
    """)

    # pod lifecycle state table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pod_state (
        pod TEXT PRIMARY KEY,
        state TEXT
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------
# Insert storage metrics
# ------------------------------------------------

def insert_metric(timestamp, pod, used, total):

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO storage_metrics
        (timestamp, pod, storage_used, total_storage)
        VALUES (?, ?, ?, ?)
        """,
        (timestamp, pod, used, total)
    )

    conn.commit()
    conn.close()


# ------------------------------------------------
# Set pod lifecycle state
# ------------------------------------------------

def set_state(pod, state):

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO pod_state (pod, state)
        VALUES (?, ?)
        """,
        (pod, state)
    )

    conn.commit()
    conn.close()


# ------------------------------------------------
# Get pod lifecycle state
# ------------------------------------------------

def get_state(pod):

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT state FROM pod_state
        WHERE pod=?
        """,
        (pod,)
    ).fetchone()

    conn.close()

    # default state
    if row:
        return row[0]

    return "ACTIVE"


# ------------------------------------------------
# Optional helper (good for debugging)
# ------------------------------------------------

def get_all_states():

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT pod, state FROM pod_state"
    ).fetchall()

    conn.close()

    return rows
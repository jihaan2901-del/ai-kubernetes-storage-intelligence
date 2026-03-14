import redis
import pandas as pd
import os

r = redis.Redis(host="localhost", port=30007)
r.flushall()

print("Redis storage cleared")

FILE_PATH = "../data/storage.csv"

if os.path.exists(FILE_PATH):

    df = pd.read_csv(FILE_PATH)

    df.loc[df["pod"].str.contains("redis"), "storage_used"] = 0.1

    df.to_csv(FILE_PATH, index=False)

    print("Redis storage value reset in dataset")
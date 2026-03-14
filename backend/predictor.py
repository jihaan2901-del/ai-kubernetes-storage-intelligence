import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

FILE_PATH = "data/storage.csv"


def predict_full_time(pod):

    df = pd.read_csv(FILE_PATH)

    pod_df = df[df["pod"] == pod]

    if len(pod_df) < 10:
        return "Collecting data..."

    latest = pod_df.iloc[-1]

    if latest["storage_used"] >= latest["total_storage"]:
        return "Disk already full"

    X = pod_df["timestamp"].values.reshape(-1, 1)
    y = pod_df["storage_used"].values

    model = LinearRegression()
    model.fit(X, y)

    total = latest["total_storage"]
    last_time = latest["timestamp"]

    # predict for next 7 days
    future_times = np.linspace(last_time, last_time + 3600 * 24 * 7, 500)

    predictions = model.predict(future_times.reshape(-1, 1))

    for t, p in zip(future_times, predictions):

        if p >= total:

            seconds = t - last_time
            minutes = seconds / 60
            hours = minutes / 60

            if hours > 24:
                days = hours / 24
                return f"{round(days,2)} days"

            return f"{round(minutes,2)} minutes (~{round(hours,2)} hours)"

    return "Not predictable yet"
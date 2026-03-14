from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from predictor import predict_full_time

FILE_PATH = "data/storage.csv"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/pods")
def get_pods():

    if not os.path.exists(FILE_PATH):
        return {"pods": []}

    df = pd.read_csv(FILE_PATH)

    pods = []

    for pod in df["pod"].unique():

        latest = df[df["pod"] == pod].iloc[-1]

        used = float(latest["storage_used"])
        total = float(latest["total_storage"])

        pod_history = df[df["pod"] == pod][["timestamp","storage_used"]]

        history = [
            {
                "timestamp": float(row["timestamp"]),
                "storage_used": float(row["storage_used"])
            }
            for _, row in pod_history.iterrows()
        ]

        pods.append({
            "name": str(pod),
            "used": used,
            "total": total,
            "remaining": float(total - used),
            "prediction": str(predict_full_time(pod)),
            "history": history
        })

    return {"pods": pods}
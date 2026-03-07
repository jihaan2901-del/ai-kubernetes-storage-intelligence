import streamlit as st
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh
from backend.predictor import predict_full_time

FILE_PATH = "data/storage.csv"

st.set_page_config(page_title="AI Kubernetes Storage Intelligence", layout="wide")

st_autorefresh(interval=5000)

st.title("AI Kubernetes Storage Intelligence")

if not os.path.exists(FILE_PATH):
    st.write("Waiting for data...")
    st.stop()

df = pd.read_csv(FILE_PATH)

df["time"] = pd.to_datetime(df["timestamp"], unit="s")

pods = df["pod"].unique()

st.metric("Containers Monitored", len(pods))

for pod in pods:

    latest = df[df["pod"] == pod].iloc[-1]

    with st.expander(pod):

        used = latest["storage_used"]
        total = latest["total_storage"]

        remaining = total - used

        col1, col2, col3 = st.columns(3)

        col1.metric("Storage Used (GB)", round(used,2))
        col2.metric("Total Storage (GB)", total)
        col3.metric("Remaining Storage (GB)", round(remaining,2))

        st.progress(min(used / total,1.0))

        prediction = predict_full_time(pod)

        st.info(f"AI Prediction: Disk may be full in {prediction}")

        pod_df = df[df["pod"] == pod]

        st.line_chart(pod_df.set_index("time")["storage_used"])
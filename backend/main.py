import threading
import uvicorn
from scheduler import start_collector
from api import app
from db import init_db

# initialize database
init_db()

# start scheduler thread
@app.on_event("startup")
def start_scheduler_thread():

    print("🚀 Starting collector + autoscaler scheduler")

    thread = threading.Thread(target=start_collector)

    thread.daemon = True

    thread.start()


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
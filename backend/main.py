import threading
from scheduler import start_collector
from api import app
import uvicorn


def start_scheduler():
    print("Starting collector thread")
    start_collector()


thread = threading.Thread(target=start_scheduler)
thread.daemon = True
thread.start()

uvicorn.run(app, host="0.0.0.0", port=8000)
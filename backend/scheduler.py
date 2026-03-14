import schedule
import time
from collector import collect_data


def start_collector():

    schedule.every(5).seconds.do(collect_data)

    while True:
        schedule.run_pending()
        time.sleep(1)
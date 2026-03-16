import schedule
import time
from collector import collect_data
from scaler import check_and_scale


def start_collector():

    schedule.every(5).seconds.do(collect_data)
    schedule.every(10).seconds.do(check_and_scale)

    while True:

        schedule.run_pending()
        time.sleep(1)
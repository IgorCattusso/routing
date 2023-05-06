from apscheduler.schedulers.background import BackgroundScheduler
import time


scheduler = BackgroundScheduler()
# scheduler.add_job(test_func, 'interval', seconds=30)
time.sleep(1)
# scheduler.add_job(test_func2, 'interval', seconds=30)
scheduler.start()


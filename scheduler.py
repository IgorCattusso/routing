from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import zoneinfo
from datetime import datetime
import tzlocal
from models import Users, UsersQueue
from sqlalchemy.orm import Session
from app import engine


scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
scheduler.remove_all_jobs()


def disconnect_all_users():
    with Session(engine) as db_session:
        Users.disconnect_all_users(db_session)
        UsersQueue.remove_all_users_from_queue(db_session)
        db_session.commit()


scheduler.add_job(disconnect_all_users, "cron", hour="23", minute="59", second="59")
# scheduler.add_job(test_func, 'interval', seconds=30)

scheduler.start()

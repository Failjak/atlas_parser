import dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient
from pytz import utc

from services.mongo.settings import MongoSettings

dotenv.load_dotenv(".env")

mongo_client = MongoClient(MongoSettings().conn_url)

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = AsyncIOScheduler(job_defaults=job_defaults, timezone=utc)

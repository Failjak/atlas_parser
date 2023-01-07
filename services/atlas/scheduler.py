import dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient
from pytz import utc

from services.mongo.settings import mongo_settings

dotenv.load_dotenv(".env")

mongo_client = MongoClient(mongo_settings.conn_url)

# jobstores = {
#     'mongo': MongoDBJobStore(client=mongo_client),
# }
# executors = {
#     'default': ThreadPoolExecutor(20),
#     'processpool': ProcessPoolExecutor(5)
# }
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = AsyncIOScheduler(job_defaults=job_defaults, timezone=utc)

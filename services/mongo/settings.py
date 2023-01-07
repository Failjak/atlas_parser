import os

from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    conn_url: str = "mongodb://{host}:{port}/{database}"
    database: str = "atlas-parser"
    params_collection: str = "params"


if os.environ.get("IS_HEROKU", None):
    mongo_settings = MongoSettings(
        conn_url=os.environ.get("CONN_URL"),
        database=os.environ.get("MONGO_DATABASE"),
        params_collection=os.environ.get("MONGO_PARAMS_COLLECTION"),
    )
else:
    mongo_settings = MongoSettings(_env_file='.env')

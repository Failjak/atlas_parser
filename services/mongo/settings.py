from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    conn_url: str = "mongodb://{host}:{port}/{database}"
    database: str = "atlas-parser"
    params_collection: str = "params"

from typing import Any, Mapping

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from services.atlas.dto import LookingTripParams
from services.mongo.settings import MongoSettings


class Mongo:
    def __init__(self, settings: MongoSettings):
        self._settings = settings

    def get_client(self) -> MongoClient:
        return MongoClient(self._settings.conn_url,)

    def get_database(self) -> Database[Mapping[str, Any] | Any]:
        return self.get_client()[self._settings.database]

    def get_collection(self, collection_name: str) -> Collection[Mapping[str, Any] | Any]:
        return self.get_database()[collection_name]

    def put_param(self, data: Mapping[str, Any] | Any):
        return self.get_collection(self._settings.params_collection).insert_one(data).inserted_id

    def update_param(self, param_id: str | ObjectId, data: Mapping[str, Any] | Any):
        self.get_collection(self._settings.params_collection).update_one({"_id": ObjectId(param_id)}, {"$set": data})

    def get_params(self, chat_id: str) -> Mapping[str, Any] | Any:
        params = self.get_collection(self._settings.params_collection).find({"chat_id": chat_id})
        return [
            LookingTripParams(
                id=param.get("_id"),
                chat_id=param.get("chat_id"),
                departure_city=param.get("departure_city"),
                arrival_city=param.get("arrival_city"),
                date=param.get("date"),
                interval=param.get("interval"),
                # state=param.get("state"),
            ) for param in params
        ] if params else []

    def retrieve_param(self, param_id: str) -> Mapping[str, Any] | Any:
        param = self.get_collection(self._settings.params_collection).find_one({"_id": ObjectId(param_id)})
        return LookingTripParams(
                id=param.get("_id"),
                chat_id=param.get("chat_id"),
                departure_city=param.get("departure_city"),
                arrival_city=param.get("arrival_city"),
                date=param.get("date"),
                interval=param.get("interval"),
                # state=param.get("state"),
            )

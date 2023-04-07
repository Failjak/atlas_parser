from typing import Any, Mapping

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from bot.constants import LookingTripState
from bot.services.trip_search import change_searching_trip_state
from services.atlas.dto import LookingTripParams
from services.mongo.settings import MongoSettings


class Mongo:
    def __init__(self, settings: MongoSettings):
        self._settings = settings

    def get_client(self) -> MongoClient:
        return MongoClient(self._settings.conn_url, )

    def get_database(self) -> Database[Mapping[str, Any] | Any]:
        return self.get_client()[self._settings.database]

    def get_collection(self, collection_name: str) -> Collection[Mapping[str, Any] | Any]:
        return self.get_database()[collection_name]

    def put_trip(self, data: Mapping[str, Any] | Any):
        return self.get_collection(self._settings.params_collection).insert_one(data).inserted_id

    def update_trip(self, trip_id: str | ObjectId, data: Mapping[str, Any] | Any):  # TODO return type
        return self.get_collection(self._settings.params_collection).update_one({"_id": ObjectId(trip_id)},
                                                                                {"$set": data})

    def retrieve_trips_params(self, chat_id: str) -> Mapping[str, Any] | Any:
        params = self.get_collection(self._settings.params_collection).find({"chat_id": chat_id})
        return [
            LookingTripParams(
                id=param.get("_id"),
                chat_id=param.get("chat_id"),
                departure_city=param.get("departure_city"),
                arrival_city=param.get("arrival_city"),
                date=param.get("date"),
                interval=param.get("interval"),
                state=param.get("state"),
            ) for param in params
        ] if params else []

    def retrieve_trip_params(self, trip_id: str) -> Mapping[str, Any] | Any:
        param = self.get_collection(self._settings.params_collection).find_one({"_id": ObjectId(trip_id)})
        return LookingTripParams(
            id=param.get("_id"),
            chat_id=param.get("chat_id"),
            departure_city=param.get("departure_city"),
            arrival_city=param.get("arrival_city"),
            date=param.get("date"),
            interval=param.get("interval"),
            state=LookingTripState.get_by_value(param.get('state')),
        )

    def update_trip_state(self, trip_id: str) -> LookingTripParams:
        trip: LookingTripParams = self.retrieve_trip_params(trip_id)
        new_state: LookingTripState = change_searching_trip_state(trip.state)

        self.update_trip(trip_id, data={"state": new_state.value})
        return self.retrieve_trip_params(trip_id)

from dataclasses import dataclass, asdict
from datetime import date, time
from types import NoneType
from typing import List

from bson import ObjectId

from bot.constants import LookingTripState


@dataclass
class City:
    id: str
    description: str
    country: str
    name: str

    dict = asdict

    def __hash__(self):
        return hash((self.id, self.description, self.country, self.name))


@dataclass
class Trip:
    name: str
    free_seats: int
    departure_time: time | None
    arrival_time: time | None
    price: int
    currency: str

    def __str__(self):
        return f"{self.name}, Мест: {self.free_seats}, Цена: {self.price} {self.currency}; " \
               f"{self.departure_time}->{self.arrival_time}"


@dataclass
class DateTrips:
    date: date
    trip_count: int
    trips: List[Trip]

    def __str__(self):
        trips_str = ""
        for trip in self.trips[:5]:
            trips_str += trip.__str__() + "\n"
        return f"{self.date.__str__()} Кол-во маршруток: {self.trip_count}\nМаршруты:\n{trips_str}..."


@dataclass
class LookingTripParams:
    departure_city: City
    arrival_city: City
    date: date | str
    interval: int
    state: LookingTripState = None
    id: ObjectId | str = None
    chat_id: str | None = None

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = date.fromisoformat(self.date)
        if isinstance(self.departure_city, dict):
            self.departure_city = City(**self.departure_city)
        if isinstance(self.arrival_city, dict):
            self.arrival_city = City(**self.arrival_city)
        # if isinstance(self.state, NoneType):
        #     from bot.services.trip_search import is_job_running
        #     self.state = is_job_running(self)

    def __hash__(self):
        return hash((self.id, self.departure_city, self.arrival_city, self.date, self.interval))

    def dict(self):
        dicted = asdict(self)
        dicted["date"] = self.date.strftime("%Y-%m-%d")
        dicted["state"] = self.state.value
        dicted.pop("id")
        return dicted

    @property
    def full_path(self):
        return f"{self.date.strftime('%-d %b')} " \
               f"{self.departure_city.name.capitalize()} --> {self.arrival_city.name.capitalize()}"

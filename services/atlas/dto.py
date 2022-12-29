from dataclasses import dataclass
from datetime import date, time
from typing import List


@dataclass
class City:
    id: str
    description: str
    country: str
    name: str


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

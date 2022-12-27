import datetime

from dataclasses import dataclass


@dataclass
class ParserDto:
    departure_place: str
    arrival_place: str
    date: datetime.date
    interval: int

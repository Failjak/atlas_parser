import datetime

from dataclasses import dataclass, asdict


@dataclass
class ParserDto:
    send_only_if_exist: bool
    departure_place: str
    arrival_place: str
    date: datetime.date
    interval: int

    dict = asdict

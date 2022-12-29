from enum import Enum

DEFAULT_INTERVAL = 10


class EnumWithGet(Enum):
    @classmethod
    def get(cls, name: str):
        try:
            return cls[name.upper()]
        except KeyError:
            return None


class ConfigureButtons(EnumWithGet):
    INTERVAL = "Интервал запросов"


class ConfigureInterval(EnumWithGet):
    PER_4_MINUTES = "Каждые 4 минуты"
    PER_10_MINUTES = "Каждые 10 минуты"
    PER_15_MINUTES = "Каждые 15 минуты"
    PER_30_MINUTES = "Каждые 30 минуты"
    PER_60_MINUTES = "Каждые 60 минут"

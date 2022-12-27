from enum import Enum

DEFAULT_INTERVAL = 5


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
    PER_0_MINUTES = "Каждые 0 минуты"
    PER_3_MINUTES = "Каждые 3 минуты"
    PER_5_MINUTES = "Каждые 5 минуты"
    PER_10_MINUTES = "Каждые 10 минуты"
    PER_30_MINUTES = "Каждые 30 минуты"
    PER_60_MINUTES = "Каждые 60 минут"

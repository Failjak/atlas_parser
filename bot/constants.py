from enum import Enum

DEFAULT_INTERVAL = 10


class EnumWithGet(Enum):
    @classmethod
    def get(cls, name: str):
        try:
            return cls[name.upper()]
        except KeyError:
            return None

    @classmethod
    def get_by_value(cls, value: str):
        try:
            return cls.__call__(value)
        except ValueError:
            return None

    @classmethod
    def all(cls):
        for item in cls:
            yield item.name, item.value


class ConfigureButtons(EnumWithGet):
    INTERVAL = "Интервал запросов"
    STATE = "Статус"


class ConfigureInterval(EnumWithGet):
    PER_1_MINUTES = "Каждую минуту"
    PER_4_MINUTES = "Каждые 4 минуты"
    PER_10_MINUTES = "Каждые 10 минуты"
    PER_15_MINUTES = "Каждые 15 минуты"
    PER_30_MINUTES = "Каждые 30 минуты"
    PER_60_MINUTES = "Каждые 60 минут"


class LookingTripState(EnumWithGet):
    ON = "ON"
    OFF = "OFF"


class TripConfigureType(EnumWithGet):
    INTERVAL = "INTERVAL"
    STATE = "STATE"

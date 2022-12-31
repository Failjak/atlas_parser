import datetime
from datetime import datetime
from typing import List, Dict

from services.atlas.api import API
from services.atlas.constants import ATLAS_NAME_TO_ID
from services.atlas.dto import City, DateTrips, Trip
from services.atlas.exceptions import InvalidCity
from services.atlas.types import CityType


class AtlasAPI(API):
    search_url = "https://atlasbus.by/api/search?from_id={}&to_id={}&calendar_width=30&date={}&passengers=1"
    info_url = "https://atlasbus.by/api/search/suggest?user_input=&from_id={}&to_id={}&locale=ru"

    def __init__(self):
        pass

    async def get_all_trips(self, departure_city: City, arrival_city: City, date: datetime.date) -> DateTrips | str:
        url = self.search_url.format(departure_city.id, arrival_city.id, date.strftime("%Y-%m-%d"))
        response = await self.send_arequest(url)

        calendar = response.get("calendar")
        rides = response.get("rides")

        for day in calendar:
            if day.get('date') != date.strftime("%Y-%m-%d"):
                continue

            if day.get("rideCount") == 0:
                return "Нет билетов"
            if not day.get("minPrices"):
                return "Нет мест"

            trips = self.get_rides_by_date(rides, date)
            return DateTrips(date=date, trips=trips, trip_count=day.get("rideCount"))

    @staticmethod
    def get_rides_by_date(rides: List, date: datetime.date) -> List[Trip]:
        trips = []
        for ride in rides:
            ride_date_str = ride.get('arrival')
            ride_all_date = datetime.strptime(ride_date_str, '%Y-%m-%dT%H:%M:%S')
            ride_date, ride_time = ride_all_date.date(), ride_all_date.time()

            if ride_date == date:
                trip = Trip(
                    name=ride.get("name"),
                    free_seats=ride.get("freeSeats"),
                    departure_time=None,
                    arrival_time=None,
                    price=ride.get("price"),
                    currency=ride.get("currency"),
                )
                trips.append(trip)

        return trips

    # async def get_all_departure_cities(self) -> List[City]:
    #     json_cities = await self.get_info_response(self.info_url)
    #     cities = [City(**js_city) for js_city in json_cities]
    #     return cities

    # async def get_all_arrival_cities(self, from_id: str) -> List[City]:
    #     json_cities = await self.get_info_response(self.info_url, from_id=from_id)
    #     cities = [City(**js_city) for js_city in json_cities]
    #     return cities

    async def get_all_departure_cities_as_dict(self) -> Dict:
        json_cities = await self.get_info_response(self.info_url)
        return {js_city.get('name'): City(**js_city) for js_city in json_cities}

    async def get_all_arrival_cities_as_dict(self, from_id: str) -> Dict:
        json_cities = await self.get_info_response(self.info_url, from_id=from_id)
        return {js_city.get('name'): City(**js_city) for js_city in json_cities}

    async def get_city_by_name(self, city_name: str, city_type: CityType, **kwargs):
        if city_type == CityType.DEPARTURE:
            dict_cities = await self.get_all_departure_cities_as_dict()
        else:
            dict_cities = await self.get_all_arrival_cities_as_dict(from_id=kwargs.get("from_id"))

        if city := ATLAS_NAME_TO_ID.get(city_name.capitalize()) or dict_cities.get(city_name.capitalize()):
            return city

        raise InvalidCity

    async def get_info_response(self, url, **kwargs):
        return await self.send_arequest(url.format(kwargs.get("from_id", ""), kwargs.get("to_id", "")))

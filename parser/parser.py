import datetime
from typing import List, Optional

import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag
from loguru import logger

from bot.errors import InvalidUrlException, TicketsNotFoundException
from parser.dto import ParserDto
from parser.settings import ParserSettings

file_name = "index.html"


async def get_html_via_url(url):
    async with aiohttp.request("get", url) as resp:
        return await resp.text()


def write_html_to_file(html):
    with open(file_name, "w") as f:
        f.write(html)


def get_html_form_file():
    with open(file_name, "r") as f:
        return f.read()


def find_all_trips(html) -> ResultSet:
    soup = BeautifulSoup(html, 'html.parser')
    main_div = soup.find("div", {"class": "MuiGrid-root MuiGrid-item MuiGrid-grid-md-8 MuiGrid-grid-lg-9"})
    looking_classes = main_div.div.get("class")
    return main_div.find_all("div", class_=looking_classes)


def find_non_empty_seats(trips: ResultSet) -> Optional[List]:
    seats = []

    for trip in trips:
        if trip.h3 and trip.h3.text == "Билеты не найдены":
            raise TicketsNotFoundException

        try:
            seats_text = trip.div.div.find("button").text
        except AttributeError:
            if trip.div.text == "Рейсов не найдено": raise InvalidUrlException
            seats_text = trip.div.div.find_next_sibling("div").find("button").text

        if seats_text != 'Нет мест':
            seats.append(trip.div.div.div)

    return seats


def generate_info_from_trip(trip: Tag):
    info = dict()
    leave_time_div: Tag = trip.div
    info["leave_time"] = leave_time_div.div.div.text

    arrival_time_div = leave_time_div.find_next_sibling("div")
    info["arrival_time"] = arrival_time_div.div.div.text

    price_and_seats_div = arrival_time_div.find_next_sibling("div")
    info["price"] = price_and_seats_div.div.div.text
    info["seats"] = price_and_seats_div.div.find_all("p")[1].text
    return info


def generate_info_from_trip_v2(trip: Tag):
    leave_time_div: Tag = trip.div
    leave_time = leave_time_div.div.div.text

    arrival_time_div = leave_time_div.find_next_sibling("div")
    arrival_time = arrival_time_div.div.div.text

    price_and_seats_div = arrival_time_div.find_next_sibling("div")
    price = price_and_seats_div.div.div.text
    seats = price_and_seats_div.div.find_all("p")[1].text
    return f"Leave time: {leave_time}, arrival time: {arrival_time}; Count of seats: {seats}, price: {price}\n"


async def parse(url, **kwargs):
    if kwargs.get("debug"):
        html = get_html_form_file()
    else:
        logger.log("PARSER", "Send request")
        html = await get_html_via_url(url)
        if kwargs.get("write_to_file"): write_html_to_file(html)

    trips: ResultSet = find_all_trips(html)
    available_trips = find_non_empty_seats(trips)

    logger.log("PARSER", "Info generating")

    if not available_trips:
        return None

    infos = ""
    for trip in available_trips:
        infos += generate_info_from_trip_v2(trip)

    msg = f"Number of available trips: {len(available_trips)}\n{infos}"
    return f"{datetime.datetime.now().strftime('%m/%d, %H:%M:%S')} - {msg}"


async def run_parser(settings: ParserSettings, params: ParserDto, **kwargs):
    url = settings.url.format(params.departure_place.capitalize(), params.arrival_place.capitalize(), params.date)
    logger.log("PARSER", f"URL: {url}")
    return await parse(url)

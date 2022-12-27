import asyncio
import datetime

import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag
from loguru import logger

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


def find_non_empty_seats(trips: ResultSet):
    seats = []

    for trip in trips:
        seats_text = trip.div.div.find("button").text
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
        logger.log(0, "Send request")
        html = await get_html_via_url(url)
        if kwargs.get("write_to_file"): write_html_to_file(html)

    trips: ResultSet = find_all_trips(html)
    available_trips = find_non_empty_seats(trips)

    logger.log(0, "Info generating")

    infos = ""
    for trip in available_trips:
        infos += generate_info_from_trip_v2(trip)

    msg = f"Number of available trips: {len(available_trips)}\n{infos}"

    if not kwargs.get("only_if_exist"):
        logger.success(msg)
        return f"{datetime.datetime.now().strftime('%m/%d, %H:%M:%S')} - {msg}"
    elif len(available_trips):
        logger.success(msg)
        return f"{datetime.datetime.now().strftime('%m/%d, %H:%M:%S')} - {msg}"


async def run_parser(settings: ParserSettings, params: ParserDto, **kwargs):
    url = settings.url.format(params.departure_place, params.arrival_place, params.date)

    try:
        while True:
            yield await parse(url, only_if_exist=True)
            await asyncio.sleep(params.interval)
    except KeyboardInterrupt:
        logger.info("Stop Atlas Parser")

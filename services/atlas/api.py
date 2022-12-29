import requests
import aiohttp

from services.atlas.exceptions import TooFrequentRequests


class API:
    @staticmethod
    def send_request(url):
        return requests.request("get", url)

    @staticmethod
    async def send_arequest(url):
        async with aiohttp.request("get", url) as resp:
            try:
                return await resp.json()
            except AttributeError:
                raise TooFrequentRequests

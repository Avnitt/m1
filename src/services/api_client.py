import os
import httpx
import logging
from dotenv import load_dotenv

from ..utils.processer import process_event_data, process_market_data

logging.basicConfig(level=logging.INFO)

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
X_RAPIDAPI_KEY = os.getenv("X_RAPIDAPI_KEY")

class APIClient:
    """
    A reusable HTTP client for Betfair API using httpx.AsyncClient.
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.headers = {
            "x-rapidapi-key": X_RAPIDAPI_KEY,
            "x-rapidapi-host": "betfair-sports-casino-live-tv-result-odds.p.rapidapi.com",
        }
        self.timeout = 10
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=self.timeout)

    async def fetch_events(self) -> httpx.Response | None:
        try:
            response = await self.client.get("/v3/front", params={"id": "4"})
            response.raise_for_status()
            logging.info(f"Fetched events successfully: {response.status_code}")
            return process_event_data(response.json())
        except Exception as e:
            logging.error(f"Error fetching events: {e}")
            return None

    async def fetch_markets(self, event_id: str) -> httpx.Response | None:
        try:
            response = await self.client.get("/GetSession/", params={"eventid": event_id})
            logging.info(response.json())
            response.raise_for_status()
            logging.info(f"Fetched markets successfully: {response.status_code}")
            return process_market_data(response.json())
        except Exception as e:
            logging.error(f"Error fetching markets: {e}")
            return None

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
import json
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from dotenv import load_dotenv

from .api_client import APIClient

load_dotenv()

POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", 10))
logging.basicConfig(level=logging.INFO)

class SchedulerService:
    def __init__(self, app: FastAPI):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logging.info("✅ Scheduler started")

    def add_event_job(self):
        if not self.scheduler.get_job("fetch_events"):
            self.scheduler.add_job(
                self._poll_fetch_events,
                trigger=IntervalTrigger(minutes=POLLING_INTERVAL),
                id="fetch_events",
                name="Periodic Event Fetch"
            )
            logging.info("Event polling job added")

    def add_market_job(self, event_id: str):
        job_id = f"fetch_market_{event_id}"
        if not self.scheduler.get_job(job_id):
            self.scheduler.add_job(
                self._poll_fetch_markets,
                args=[event_id],
                trigger=IntervalTrigger(minutes=POLLING_INTERVAL),
                id=job_id,
                name=f"Market Fetch for {event_id}"
            )
            logging.info(f"Market polling job added for event {event_id}")

    def remove_market_fetch_job(self, event_id: str):
        job_id = f"fetch_market_{event_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logging.info(f"Market polling job removed for event {event_id}")

    def stop(self):
        logging.info("📛 Scheduler stopping...")
        self.scheduler.shutdown(wait=False)

    async def _poll_fetch_events(self):
        logging.info("Polling events...")
        try:
            async with APIClient() as client:
                response = await client.fetch_events()
                if response:
                    redis = self.app.state.redis_client
                    await redis.publish("events_channel", json.dumps(response))
                    await redis.set("events", json.dumps(response))
                    logging.info("Events published successfully")
                else:
                    logging.warning("No events fetched")
        except Exception as e:
            logging.error(f"Error fetching events: {e}")

    async def _poll_fetch_markets(self, event_id: str):
        logging.info(f"Polling markets for event {event_id}...")
        try:
            async with APIClient() as client:
                response = await client.fetch_markets(event_id=event_id)
                if response:
                    redis = self.app.state.redis_client
                    await redis.publish(f"markets_channel:{event_id}", json.dumps(response))
                    await redis.set(f"markets:{event_id}", json.dumps(response))
                    logging.info(f"Markets for {event_id} published successfully")
                else:
                    logging.warning(f"No markets fetched for {event_id}")
        except Exception as e:
            logging.error(f"Error fetching markets for {event_id}: {e}")
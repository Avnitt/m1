import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from .api_client import APIClient
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

class SchedulerService:
    def __init__(self, app: FastAPI):
        self.app = app
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def add_event_job(self):
        if not self.scheduler.get_job("fetch_events"):
            self.scheduler.add_job(
                self._poll_fetch_events,
                trigger=IntervalTrigger(seconds=20),
                id="fetch_events",
                name="Periodic Event Fetch"
            )

    def add_market_job(self, event_id: str):
        job_id = f"fetch_market_{event_id}"
        if self.scheduler.get_job(job_id):
            return

        self.scheduler.add_job(
            self._poll_fetch_markets,
            args=[event_id],
            trigger=IntervalTrigger(seconds=20),
            id=job_id,
            name=f"Market Fetch for {event_id}"
        )
    
    def remove_market_fetch_job(self, event_id: str):
        job_id = f"fetch_market_{event_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def stop(self):
        logging.info("🛑 Scheduler stopping")
        self.scheduler.shutdown(wait=False)

    async def _poll_fetch_events(self):
        logging.info("Fetching events...")
        try:
            async with APIClient() as client:
                response = await client.fetch_events()
                if response:
                    logging.info('Fetched events successfully')
                    redis = self.app.state.redis_client
                    await redis.publish("events_channel", json.dumps(response))
                    await redis.set("events", json.dumps(response))
                    logging.info("Published events successfully")
                else:
                    logging.error("Failed to fetch events")
        except Exception as e:
            logging.error(f"Error during event fetching: {e}")

    async def _poll_fetch_markets(self, event_id: str):
        logging.info(f"Fetching markets for {event_id}...")
        try:
            async with APIClient() as client:
                response = await client.fetch_markets(event_id=event_id)
                if response:
                    logging.info(f"Fetched markets successfully")
                    redis = self.app.state.redis_client
                    await redis.publish(f"markets_channel:{event_id}", json.dumps(response))
                    await redis.set(f"markets:{event_id}", json.dumps(response))
                    logging.info(f"Published markets successfully")
                else:
                    logging.error("Failed to fetch markets")
        except Exception as e:
            logging.error(f"Error during markets fetching: {e}")
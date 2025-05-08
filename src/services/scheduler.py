import asyncio
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from .redis_client import redis_client
from .api_client import APIClient

logging.basicConfig(level=logging.INFO)

async def poll_fetch_events():
    """
    This function is called periodically to fetch events.
    """
    logging.info("Fetching events...")
    try:
        async with APIClient() as client:
            response = await client.fetch_events()
            if response:
                logging.info('Fetched events succesfully')
                await redis_client.publish("events_channel", json.dumps(response))
                await redis_client.set("events", json.dumps(response))

                logging.info("Published events succesfully")
            else:
                logging.error("Failed to fetch events")
    except Exception as e:
        logging.error(f"Error during event fetching: {e}")

async def poll_fetch_markets(event_id: str):
    """
    This function is called periodically to fetch events.
    """
    logging.info("Fetching events...")
    try:
        async with APIClient() as client:
            response = await client.fetch_markets(event_id=event_id)
            if response:
                logging.info(f"Fetched markets succesfully")
                await redis_client.publish(f"markets_channel:{event_id}", json.dumps(response))
                await redis_client.set(f"markets:{event_id}", json.dumps(response))
                logging.info(f"Published markets succesfully")
            else:
                logging.error("Failed to fetch markets")
    except Exception as e:
        logging.error(f"Error during markets fetching: {e}")

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def add_event_job(self):
        if not self.scheduler.get_job("fetch_events"):
            self.scheduler.add_job(
                poll_fetch_events,
                trigger=IntervalTrigger(seconds=20),
                id="fetch_events",
                name="Periodic Event Fetch"
            )

    def add_market_job(self, event_id: str):
        job_id = f"fetch_market_{event_id}"
        if self.scheduler.get_job(job_id):
            return

        self.scheduler.add_job(
            poll_fetch_markets,
            args=[event_id],
            trigger=IntervalTrigger(seconds=20),
            id=f"fetch_market_{event_id}",
            name=f"Market Fetch for {event_id}"
        )
    
    def remove_market_fetch_job(self, event_id: str):
        job_id = f"fetch_market_{event_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    def stop(self):
        logging.info("🛑 Scheduler stopping")
        self.scheduler.shutdown(wait=False)
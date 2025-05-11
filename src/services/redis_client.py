import os
import redis.asyncio as redis
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

class RedisClient:
    def __init__(self):
        self.redis_url = REDIS_URL
        self.redis_client = redis.from_url(
            url=self.redis_url,
            decode_responses=True
        )
        self.pubsubs = {}

    async def get(self, key: str):
        """
        Get data from Redis cache.
        """
        try:
            data = await self.redis_client.get(key)
            if data:
                logging.info(f"Data fetched from Redis for key: {key}")
            return data
        except Exception as e:
            logging.error(f"Error fetching data from Redis for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ex: int = 600):
        """
        Set data in Redis cache with optional expiration time (in seconds).
        """
        try:
            await self.redis_client.set(key, value, ex=ex)
            logging.info(f"Data set in Redis for key: {key}")
        except Exception as e:
            logging.error(f"Error setting data in Redis for key {key}: {e}")

    async def delete(self, key: str):
        """
        Delete data from Redis cache.
        """
        try:
            await self.redis_client.delete(key)
            logging.info(f"Data deleted from Redis for key: {key}")
        except Exception as e:
            logging.error(f"Error deleting data from Redis for key {key}: {e}")

    async def publish(self, channel: str, message: str):
        """
        Publish a message to a Redis channel.
        """
        try:
            await self.redis_client.publish(channel, message)
            logging.info(f"Message published to Redis channel: {channel}")
        except Exception as e:
            logging.error(f"Error publishing message to Redis channel {channel}: {e}")

    async def new_pubsub(self, channel: str):
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(channel)
        self.pubsubs[channel] = pubsub
        return pubsub

    async def close(self):
        try:
            for pubsub in self.pubsubs.values():
                await pubsub.unsubscribe()
                await pubsub.close()
            await self.redis_client.close()
            logging.info("Redis connection closed.")
        except Exception as e:
            logging.error(f"Error closing Redis connection: {e}")

# redis_client = RedisClient()
# logging.info("Redis client initialized.")
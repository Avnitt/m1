import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from utils.processer import process_event_data, process_market_data

logger = logging.getLogger("uvicorn")

class WebSocketManager:
    def __init__(self, redis_client, scheduler_service, api_client_cls):
        self.redis_client = redis_client
        self.scheduler = scheduler_service
        self.api_client_cls = api_client_cls
        self.connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        logger.info("WebSocket connected.")

    async def listen(self, websocket: WebSocket):
        try:
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)
                event_id = data.get("event_id")

                # Handle market subscription
                if event_id:
                    await self.subscribe_to_markets(event_id, websocket)
                # Handle events subscription
                else:
                    await self.subscribe_to_events(websocket)

        except WebSocketDisconnect:
            await self.disconnect_all(websocket)

    async def subscribe_to_events(self, websocket: WebSocket):
        # Add the user to the events channel and send the latest events data
        if "events" not in self.connections:
            self.connections["events"] = set()

        self.connections["events"].add(websocket)

        # Send the latest events data to WebSocket when connected
        await self.send_events_data(websocket)

        # Subscribe to events channel via Redis
        asyncio.create_task(self.pubsub_listener("events_channel", websocket))

    async def subscribe_to_markets(self, event_id: str, websocket: WebSocket):
        # Add user to the specific market channel
        if event_id not in self.connections:
            self.connections[event_id] = set()

            # Add polling job if this is the first subscriber
            self.scheduler.add_market_job(event_id)

        self.connections[event_id].add(websocket)
        logger.info(f"Added connection to {event_id} (total: {len(self.connections[event_id])})")

        # Try sending cached market data immediately
        cached = await self.redis_client.get(f"markets:{event_id}")
        if cached:
            await websocket.send_text(cached)
        else:
            # If no events data, fetch from API and send
            async with self.api_client_cls() as client:
                response = await client.fetch_markets(event_id)
                if response:
                    await websocket.send_text(json.dumps(response))
                    logger.info("Sent freshly fetched events data to WebSocket")

        # Start listening to PubSub channel
        asyncio.create_task(self.pubsub_listener(f"markets_channel:{event_id}", websocket))

    async def send_events_data(self, websocket: WebSocket):
        # Fetch latest events from Redis if available
        events_data = await self.redis_client.get("events")
        
        if events_data:
            await websocket.send_text(events_data)
            logger.info("Sent events data to WebSocket")
        else:
            # If no events data, fetch from API and send
            async with self.api_client_cls() as client:
                response = await client.fetch_events()
                if response:
                    await websocket.send_text(json.dumps({"events": response}))
                    logger.info("Sent freshly fetched events data to WebSocket")

    async def pubsub_listener(self, channel: str, websocket: WebSocket):
        pubsub = await self.redis_client.new_pubsub(channel)
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    payload = message["data"]
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_text(payload)
                    else:
                        break
        except Exception as e:
            logger.error(f"PubSub listener error for {channel}: {e}")
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    async def disconnect_all(self, websocket: WebSocket):
        to_remove = []
        for channel, websockets in self.connections.items():
            websockets.discard(websocket)
            if not websockets:
                to_remove.append(channel)
    
        for channel in to_remove:
            # Remove job for market fetch if no subscribers
            if channel.startswith("market_channel"):
                event_id = channel.split(":")[1]
                self.scheduler.remove_market_fetch_job(event_id)
            del self.connections[channel]
            logger.info(f"Removed subscription for channel: {channel}")
    
        # Avoid closing if already disconnected or disconnect was triggered by exception
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close()
                logger.info("WebSocket disconnected.")
            except Exception as e:
                logger.warning(f"Failed to close WebSocket: {e}")


import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logging.basicConfig(level=logging.INFO)

class WebSocketManager:
    def __init__(self, redis_client, scheduler_service, api_client_cls):
        self.redis_client = redis_client
        self.scheduler = scheduler_service
        self.api_client_cls = api_client_cls
        self.connections: dict[str, set[WebSocket]] = {}
        self.listener_tasks: dict[tuple[str, WebSocket], asyncio.Task] = {}
        self.ping_tasks: dict[WebSocket, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        logging.info("WebSocket connected.")
        self.ping_tasks[websocket] = asyncio.create_task(self._ping(websocket))

    async def listen(self, websocket: WebSocket):
        try:
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)
                event_id = data.get("event_id")

                if event_id:
                    await self.subscribe_to_markets(event_id, websocket)
                else:
                    await self.subscribe_to_events(websocket)

        except WebSocketDisconnect:
            await self.disconnect_all(websocket)

    async def subscribe_to_events(self, websocket: WebSocket):
        self.connections.setdefault("events", set()).add(websocket)
        await self.send_events_data(websocket)
        self._start_listener("events_channel", websocket)

    async def subscribe_to_markets(self, event_id: str, websocket: WebSocket):
        first_subscriber = event_id not in self.connections
        self.connections.setdefault(event_id, set()).add(websocket)

        if first_subscriber:
            self.scheduler.add_market_job(event_id)

        logging.info(f"Added connection to {event_id} (total: {len(self.connections[event_id])})")

        cached = await self.redis_client.get(f"markets:{event_id}")
        if cached:
            await websocket.send_text(cached)
        else:
            async with self.api_client_cls() as client:
                response = await client.fetch_markets(event_id)
                if response:
                    await websocket.send_text(json.dumps(response))
                    logging.info("Sent freshly fetched markets data to WebSocket")

        self._start_listener(f"markets_channel:{event_id}", websocket)

    async def send_events_data(self, websocket: WebSocket):
        events_data = await self.redis_client.get("events")
        if events_data:
            await websocket.send_text(events_data)
            logging.info("Sent cached events data to WebSocket")
        else:
            async with self.api_client_cls() as client:
                response = await client.fetch_events()
                if response:
                    await websocket.send_text(json.dumps({"events": response}))
                    logging.info("Sent freshly fetched events data to WebSocket")

    def _start_listener(self, channel: str, websocket: WebSocket):
        key = (channel, websocket)
        if key not in self.listener_tasks:
            task = asyncio.create_task(self._pubsub_listener(channel, websocket))
            self.listener_tasks[key] = task

    async def _pubsub_listener(self, channel: str, websocket: WebSocket):
        pubsub = await self.redis_client.new_pubsub(channel)
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    payload = message["data"]
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_text(payload)
                    else:
                        break
        except Exception as e:
            logging.error(f"PubSub listener error for {channel}: {e}")
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            self.listener_tasks.pop((channel, websocket), None)

    async def _ping(self, websocket: WebSocket):
        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                await asyncio.sleep(30)
                await websocket.send_json({"ping": "pong"})
        except Exception:
            pass  # Disconnected
        finally:
            self.ping_tasks.pop(websocket, None)

    async def disconnect_all(self, websocket: WebSocket):
        for channel, websockets in list(self.connections.items()):
            websockets.discard(websocket)
            if not websockets:
                if channel != "events":
                    self.scheduler.remove_market_fetch_job(channel)
                del self.connections[channel]
                logging.info(f"Removed subscription for channel: {channel}")

        # Cancel listener tasks
        to_cancel = [key for key in self.listener_tasks if key[1] == websocket]
        for key in to_cancel:
            task = self.listener_tasks.pop(key, None)
            if task:
                task.cancel()

        # Cancel ping
        ping_task = self.ping_tasks.pop(websocket, None)
        if ping_task:
            ping_task.cancel()

        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close()
                logging.info("WebSocket disconnected.")
            except Exception as e:
                logging.warning(f"Failed to close WebSocket: {e}")
        else:
            logging.info("WebSocket already disconnected or closed.")
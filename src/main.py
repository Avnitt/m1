from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging

from .services.api_client import APIClient
from .services.redis_client import RedisClient
from .services.scheduler import SchedulerService
from .services.websocket_handler import WebSocketManager

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis_client = RedisClient()
    app.state.scheduler = SchedulerService(app)
    app.state.scheduler.add_event_job()
    app.state.ws_manager = WebSocketManager(
        redis_client=app.state.redis_client,
        scheduler_service=app.state.scheduler,
        api_client_cls=APIClient
    )
    
    yield  # Application runs here
    
    # Cleanup on shutdown
    await app.state.redis_client.close()
    app.state.scheduler.stop()
    logging.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Betfair Real-time Data Service"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ws_manager: WebSocketManager = app.state.ws_manager
    await ws_manager.connect(websocket)
    try:
        await ws_manager.listen(websocket)
    except WebSocketDisconnect:
        await ws_manager.disconnect_all(websocket)
        logging.info("WebSocket client disconnected")
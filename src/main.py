from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

from .services.api_client import APIClient
from .services.redis_client import RedisClient
from .services.scheduler import SchedulerService
from .services.websocket_handler import WebSocketManager
from .database import create_db_and_tables
from .routers import users, auth, bet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    app.state.redis_client = RedisClient()
    app.state.scheduler = SchedulerService(app)
    app.state.scheduler.add_event_job()
    app.state.ws_manager = WebSocketManager(
        redis_client=app.state.redis_client,
        scheduler_service=app.state.scheduler,
        api_client_cls=APIClient
    )
    create_db_and_tables()

    yield
    logger.info("Shutting down application...")
    await app.state.redis_client.close()
    app.state.scheduler.stop()
    logger.info("Shutdown complete")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(bet.router)


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
        logger.info("WebSocket client disconnected")
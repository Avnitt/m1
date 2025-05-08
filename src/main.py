from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging
from services.redis_client import redis_client
from services.scheduler import SchedulerService
from services.api_client import APIClient
from services.websocket_handler import WebSocketManager

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared components
    scheduler_service = SchedulerService()
    
    # Initialize WebSocket manager
    app.state.ws_manager = WebSocketManager(
        redis_client=redis_client,
        scheduler_service=scheduler_service,
        api_client_cls=APIClient
    )
    
    # Start background tasks
    scheduler_service.add_event_job()
    
    yield  # Application runs here
    
    # Cleanup on shutdown
    await redis_client.close()
    scheduler_service.stop()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, log_level="warning", reload=True)
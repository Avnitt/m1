# 🎯 Betfair Real-time Data Service (FastAPI Backend)

This is a FastAPI-based real-time backend service designed to fetch, cache, and distribute **sports event and market data** via **WebSockets**, with background job scheduling and Redis Pub/Sub support.

---

## 🚀 Features

- 📡 WebSocket API for real-time communication
- 🔁 Background polling via APScheduler (for both events and markets)
- 🧠 Redis-based caching and pub/sub distribution
- ♻️ Smart resource usage: Only fetches markets when clients subscribe
- 📁 Modular, scalable project structure
- 🧪 Easily integrable with any frontend

---

## 🏗️ Tech Stack

- **FastAPI** – Web framework
- **Redis** – Cache and Pub/Sub
- **APScheduler** – Scheduled polling
- **WebSockets** – Real-time data updates
- **Docker (optional)** – Containerization support

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/betfair-realtime-backend.git
cd betfair-realtime-backend
````

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the root directory:

```env
REDIS_URL=redis://localhost:6379
POLLING_INTERVAL=1  # Interval in minutes
```

---

## 🧪 Running the Server

```bash
uvicorn src.main:app --reload
```

> Replace `src.main:app` with the correct import path if your main file is named differently.

---

## 🔌 WebSocket API

### Endpoint

```txt
ws://localhost:8000/ws
```

### Message Format (from Frontend → Backend)

#### To Subscribe to Events

```json
{ "type": "events" }
```

#### To Subscribe to a Market

```json
{ "type": "market", "event_id": "1234" }
```

---

### Backend → Frontend Messages

* **Events Data**:

```json
{
  "events": [
    { "id": "1234", "name": "Match A vs B", "time": "..." },
    ...
  ]
}
```

* **Markets Data**:

```json
{
  "market_id": "5678",
  "event_id": "1234",
  "odds": [...]
}
```

---

## 🧠 How It Works

1. On server start:

   * Redis client, Scheduler, and WebSocketManager are initialized in FastAPI's `lifespan`.
   * Scheduler starts polling events at intervals defined in `.env`.

2. When a WebSocket client connects:

   * If they subscribe to `"events"`, they immediately receive cached events and future updates via Redis Pub/Sub.
   * If they subscribe to a `"market"` with an `event_id`:

     * A background job is started to poll that market.
     * Market data is pushed to subscribed clients and cached in Redis.

3. When the last user leaves a market:

   * The polling job for that market is removed automatically to save resources.

---

## 🧩 Frontend Integration Guide

You can use this backend with any frontend (React, Vue, etc.).

### Sample JavaScript Client

```js
const socket = new WebSocket("ws://localhost:8000/ws");

socket.onopen = () => {
  // Subscribe to events
  socket.send(JSON.stringify({ type: "events" }));

  // Or subscribe to a specific market
  socket.send(JSON.stringify({ type: "market", event_id: "1234" }));
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};
```

---

## 📁 Project Structure

```
src/
├── main.py               # FastAPI app + lifespan
├── services/
│   ├── api_client.py     # External API calls
│   ├── redis_client.py   # Redis helper
│   ├── scheduler.py      # APScheduler logic
│   └── websocket_handler.py # WebSocketManager class
├── utils/
│   └── processer.py     # Response processer
```

---

## ✅ To Do / Contributions Welcome

* [ ] Add authentication
* [ ] Dockerize the entire stack
* [ ] Add test cases

---

## 🧑‍💻 Author

Developed by \[Avnitt]
Open to contributions and improvements!

---

## 🛡️ License

MIT License

```
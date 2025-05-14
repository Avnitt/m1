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
BASE_URL=https://betfair-sports-casino-live-tv-result-odds.p.rapidapi.com/api/
X_RAPIDAPI_KEY=
REDIS_URL=redis://localhost:6379/0
POLLING_INTERVAL=
JWT_TOKEN_SECRET=
JWT_ALGORITHM=
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
[
  {
    "event_id": "e001",
    "event_name": "Football Match 1",
    "openDate": "2025-05-15T18:00:00Z",
    "runners": [
      {
        "name": "Team A",
        "backOdds": 1.7,
        "layOdds": 1.8
      },
      {
        "name": "Team B",
        "backOdds": 2.1,
        "layOdds": 2.2
      }
    ]
  },
  {
    "event_id": "e002",
    "event_name": "Football Match 2",
    "openDate": "2025-05-16T20:00:00Z",
    "runners": [
      {
        "name": "Team X",
        "backOdds": 1.5,
        "layOdds": 1.6
      },
      {
        "name": "Team Y",
        "backOdds": 2.3,
        "layOdds": 2.4
      }
    ]
  }
]
```

* **Markets Data**:

```json
{
  "bookMaker": [
    {
      "marketId": "b456",
      "marketName": "Match Odds",
      "statusName": "OPEN",
      "minSetting": 500,
      "maxSetting": 5000,
      "sortPeriority": 1,
      "runners": [
        {
          "selectionName": "Team A",
          "selectionStatus": "ACTIVE",
          "backOdds": 1.7,
          "layOdds": 1.8
        },
        {
          "selectionName": "Team B",
          "selectionStatus": "ACTIVE",
          "backOdds": 2.1,
          "layOdds": 2.2
        }
      ]
    }
  ],
  "fancy": [
    {
      "marketId": "f123",
      "marketName": "Total Runs",
      "statusName": "ACTIVE",
      "runsNo": 125,
      "runsYes": 130,
      "oddsNo": 1.85,
      "oddsYes": 1.95,
      "minSetting": 100,
      "maxSetting": 1000,
      "sortingOrder": 1,
      "catagory": "cricket"
    },
    {
      "marketId": "f124",
      "marketName": "Wickets in First 10 Overs",
      "statusName": "ACTIVE",
      "runsNo": 2,
      "runsYes": 3,
      "oddsNo": 2.0,
      "oddsYes": 1.9,
      "minSetting": 200,
      "maxSetting": 2000,
      "sortingOrder": 2,
      "catagory": "cricket"
    },
    {
      "marketId": "f125",
      "marketName": "Powerplay Score Over/Under",
      "statusName": "ACTIVE",
      "runsNo": 45,
      "runsYes": 50,
      "oddsNo": 1.95,
      "oddsYes": 2.0,
      "minSetting": 300,
      "maxSetting": 3000,
      "sortingOrder": 3,
      "catagory": "cricket"
    }
  ]
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
src
├── __init__.py
├── database.py
├── dependencies.py
├── internal
│   ├── __init__.py
│   └── admin.py
├── main.py
├── models
│   ├── __init__.py
│   └── user.py
├── routers
│   ├── __init__.py
│   ├── auth.py
│   └── users.py
├── schemas
│   ├── __init__.py
│   └── user.py
├── services
│   ├── __init__.py
│   ├── api_client.py
│   ├── redis_client.py
│   ├── scheduler.py
│   └── websocket_handler.py
└── utils
    ├── __init__.py
    ├── hashing.py
    └── processer.py
```

---

## ✅ To Do / Contributions Welcome

* [ ] Add authentication
* [ ] Dockerize the entire stack
* [ ] Add test cases

---

## 🧑‍💻 Author

Developed by \[Avnitt]<br />
Open to contributions and improvements!

---

## 🛡️ License

MIT License
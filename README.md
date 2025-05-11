Here’s a complete `README.md` for your backend project. It includes project overview, setup, environment config, Redis/WebSocket handling, and frontend integration instructions.

---

````markdown
# 🎲 Betfair Real-Time Data Service

This project is a FastAPI-based backend for **real-time betting event and market data delivery**. It connects to a third-party API (like Betfair), processes events and markets, and delivers data to frontend clients over WebSockets. It uses Redis Pub/Sub for real-time message broadcasting and `APScheduler` to poll data periodically.

---

## 📦 Features

- 🔄 Real-time WebSocket updates for events and market data
- ⚙️ Background polling using `APScheduler`
- 🔌 Redis Pub/Sub for efficient data delivery
- 🌐 Modular FastAPI architecture
- 📡 Easily connectable to any frontend (React, Vue, etc.)

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.10+
- Redis server (local or cloud)
- Optional: `.env` file for environment variables

---

## 🔧 Installation

```bash
git clone https://github.com/your-username/betfair-realtime-service.git
cd betfair-realtime-service
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
````

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
POLLING_INTERVAL=0.5  # in minutes
```

---

## 📂 Project Structure

```bash
.
├── app/
│   ├── main.py                # FastAPI entry point with lifespan
│   ├── services/
│   │   ├── api_client.py      # API client to fetch events/markets
│   │   ├── redis_client.py    # Redis connection abstraction
│   │   ├── scheduler.py       # APScheduler background jobs
│   │   └── websocket_handler.py  # WebSocket connection handler
├── requirements.txt
└── README.md
```

---

## ▶️ Running the Server

```bash
uvicorn app.main:app --reload
```

* API will run on: `http://127.0.0.1:8000`
* WebSocket endpoint: `ws://127.0.0.1:8000/ws`

---

## 🧠 How It Works

### 1. **Lifespan Management**

On startup:

* Initializes Redis client
* Starts the event polling job
* Sets up WebSocket manager

On shutdown:

* Closes Redis connection
* Stops the scheduler gracefully

### 2. **Scheduler**

* Fetches events every `POLLING_INTERVAL`
* Fetches market data for active `event_ids`
* Publishes both to Redis channels and stores the latest snapshot in Redis keys

### 3. **WebSocket Flow**

* Clients connect to `/ws`
* Can subscribe to:

  * All `events`
  * Specific `markets` via `{ "event_id": "1234" }`
* Real-time updates are sent from Redis Pub/Sub
* Polling job is created on first subscriber, and removed when last user disconnects

---

## 💻 Frontend Integration

Any frontend (React, Vue, Angular, etc.) can connect via a WebSocket.

### 🔌 WebSocket Usage Example (JavaScript)

```javascript
const socket = new WebSocket("ws://localhost:8000/ws");

socket.onopen = () => {
  // Subscribe to events
  socket.send(JSON.stringify({}));

  // OR subscribe to specific market
  // socket.send(JSON.stringify({ event_id: "12345" }));
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("📨 Received:", data);
};

socket.onclose = () => {
  console.log("WebSocket disconnected.");
};
```

---

## 📚 API Reference

### `GET /`

Returns a health check message.

```json
{ "message": "Betfair Real-time Data Service" }
```

---

## 📤 Publishing Format (Redis PubSub)

* Events channel: `events_channel`

  * Redis Key: `events`
* Markets channel: `markets_channel:{event_id}`

  * Redis Key: `markets:{event_id}`

---

## 🧪 Testing Tips

You can use tools like:

* **Postman** for health check
* **RedisInsight** to inspect Redis keys
* **wscat** or browser console to test WebSocket

```bash
wscat -c ws://localhost:8000/ws
```

Then send:

```json
{}
```

or

```json
{ "event_id": "1234" }
```

---

## 🧹 Cleanup

* Polling jobs for a market are stopped automatically when no users are subscribed.
* Redis connections and scheduler are gracefully shut down via FastAPI lifespan context.

---

## 🤝 Contributing

PRs are welcome! Please fork the repo and open a pull request.

---

## 🪪 License

MIT License. See `LICENSE` file.

---

## 📞 Contact

For questions or support, raise an issue or email `avnit2115@gmail.com`.
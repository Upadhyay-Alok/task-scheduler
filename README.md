# 🚀 Distributed Task Scheduler (DAG Based)

A distributed task scheduler built using **FastAPI, Celery, Redis, and DAG (Directed Acyclic Graph)** execution.

---

## 🔥 Features

* Task dependency handling using DAG
* Asynchronous task execution using Celery
* Redis as message broker + status store
* Real-time task status tracking
* Retry mechanism on failure

---

## 🛠 Tech Stack

* Python
* FastAPI
* Celery
* Redis
* Docker

---

## ⚙️ How to Run

### 1. Start Redis

```bash
docker run -d -p 6379:6379 redis
```

### 2. Start Celery Worker

```bash
celery -A app.tasks worker --loglevel=info --pool=solo
```

### 3. Start FastAPI Server

```bash
python -m uvicorn app.main:app --reload
```

---

## 📌 API Endpoints

### Run Tasks

POST `/run`

### Get All Status

GET `/status`

### Get Single Task Status

GET `/status/{task_id}`

---

## 🧠 Example

Tasks:
A → B → C

Execution:
A → B → C (in order)

---

## 🎯 Output Example

```json
{
  "A": "completed",
  "B": "completed",
  "C": "completed"
}
```

---

## 💡 Future Improvements

* Dashboard UI
* Task priority scheduling
* Distributed workers
* Database integration

---

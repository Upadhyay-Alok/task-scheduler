from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import os
import threading

from app.models import Database
from app.scheduler import Scheduler

app = FastAPI()

# 🔥 Shared DB
db = Database()

# 🔥 WebSocket connections
connections = []

# 🔥 prevent multiple runs
is_running = False


# 🏠 Home
@app.get("/")
def home():
    return {"message": "Server running 🚀"}


# ❤️ Health check (NEW)
@app.get("/health")
def health():
    try:
        db.get_tasks()
        return {"status": "healthy"}
    except:
        return {"status": "error"}


# 📊 Metrics API (NEW)
@app.get("/metrics")
def metrics():
    return db.get_metrics()


# 🚀 Run tasks
@app.post("/run")
def run_tasks():
    global is_running

    if is_running:
        return {"status": "already running"}

    is_running = True

    db.clear_all()

    # 🔥 tasks
    db.add_task("A", 1)
    db.add_task("B", 2)
    db.add_task("C", 3)

    # 🔥 dependencies
    db.add_dependency("A", "B")
    db.add_dependency("B", "C")

    scheduler = Scheduler(db)

    def run_scheduler():
        global is_running
        try:
            scheduler.schedule()
        finally:
            is_running = False

    threading.Thread(target=run_scheduler, daemon=True).start()

    return {"status": "tasks started"}


# 🔄 Resume unfinished tasks (NEW)
@app.on_event("startup")
def resume_tasks():
    statuses = db.get_all_status()

    if any(s != "completed" for s in statuses.values()):
        print("🔁 Resuming unfinished tasks...")

        scheduler = Scheduler(db)

        threading.Thread(target=scheduler.schedule, daemon=True).start()


# 📊 Status APIs
@app.get("/status")
def get_status():
    return db.get_all_status()


@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    return {task_id: db.get_status(task_id)}


# 📜 Logs API
@app.get("/logs/{task_id}")
def get_logs(task_id: str):
    return db.get_logs(task_id)


# 🔥 WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connections:
            connections.remove(websocket)


# 🔥 Broadcast (safe)
async def broadcast(data: dict):
    dead = []

    for conn in connections:
        try:
            await conn.send_json(data)
        except:
            dead.append(conn)

    for d in dead:
        if d in connections:
            connections.remove(d)


# 🎨 Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    file_path = os.path.join("app", "templates", "dashboard.html")

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)
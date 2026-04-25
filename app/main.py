from fastapi import FastAPI
from app.models import Database
from app.scheduler import Scheduler

app = FastAPI()

# 🔥 IMPORTANT: shared DB (same instance)
db = Database()

@app.get("/")
def home():
    return {"message": "Server running 🚀"}

# 🚀 Run tasks
@app.post("/run")
def run_tasks():

    # 🔥 reset (clean run every time)
    db.clear_all()

    # tasks
    db.add_task("A", 1)
    db.add_task("B", 2)
    db.add_task("C", 3)

    # dependencies
    db.add_dependency("A", "B")
    db.add_dependency("B", "C")

    scheduler = Scheduler(db)
    scheduler.schedule()

    return {"status": "tasks sent to queue"}

# 🔥 Get all task statuses
@app.get("/status")
def get_status():
    return db.get_all_status()

# 🔥 Get single task status
@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    return {task_id: db.get_status(task_id)}
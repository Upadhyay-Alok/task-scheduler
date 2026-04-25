from app.celery_app import celery
from app.models import Database
import time
import random

db = Database()

@celery.task(bind=True, max_retries=3)
def execute_task(self, task_id):
    print(f"[Worker] Executing {task_id}...")

    try:
        db.update_status(task_id, "running")

        time.sleep(1)

        if random.random() < 0.2:
            raise Exception("Random failure")

        db.update_status(task_id, "completed")
        print(f"{task_id} completed ✅")

    except Exception as e:
        db.update_status(task_id, "failed")
        print(f"{task_id} failed ❌ retrying...")

        raise self.retry(exc=e, countdown=2)
from app.celery_app import celery
from app.models import Database
import time
import random

# 🔥 shared DB
db = Database()


@celery.task(bind=True, max_retries=3, soft_time_limit=10)
def execute_task(self, task_id):
    task_id = str(task_id)

    retry_count = self.request.retries

    print(f"[Worker] Executing {task_id} (Retry: {retry_count})...")

    # 🔥 idempotency (avoid duplicate execution)
    current_status = db.get_status(task_id)
    if current_status == "completed":
        print(f"{task_id} already completed, skipping...")
        return

    try:
        # 🔥 start log
        db.add_log(task_id, f"🚀 Started (Retry: {retry_count})")

        db.update_status(task_id, "running")

        start_time = time.time()

        # 🔥 simulate work
        time.sleep(1)

        # 🔥 simulate failure
        if random.random() < 0.2:
            raise Exception("Random failure")

        # 🔥 success
        db.update_status(task_id, "completed")

        duration = round(time.time() - start_time, 2)

        db.add_log(task_id, f"✅ Completed in {duration}s")

        # 🔥 metrics
        try:
            from app.redis_client import redis_client
            redis_client.incr("metric:success")
        except:
            pass

        print(f"{task_id} completed ✅")

    except Exception as e:
        db.update_status(task_id, "failed")

        db.add_log(task_id, f"❌ Failed (Retry: {retry_count})")

        print(f"{task_id} failed ❌ retrying...")

        # 🔥 metrics
        try:
            from app.redis_client import redis_client
            redis_client.incr("metric:failed")
        except:
            pass

        # 🔥 retry if limit not reached
        if retry_count < self.max_retries:
            db.add_log(task_id, "🔁 Retrying in 2 seconds...")
            raise self.retry(exc=e, countdown=2)
        else:
            db.add_log(task_id, "💀 Max retries reached")
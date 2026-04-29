from app.redis_client import redis_client
import asyncio

class Database:

    # ---------------- TASKS ---------------- #

    def add_task(self, task_id, priority):
        task_id = str(task_id)
        redis_client.hset(f"task:{task_id}", mapping={
            "priority": str(priority),
            "status": "pending"
        })

    def get_tasks(self):
        keys = redis_client.keys("task:*")
        result = []

        for key in keys:
            key = key.decode() if isinstance(key, bytes) else key
            data = redis_client.hgetall(key)

            clean = {}
            for k, v in data.items():
                k = k.decode() if isinstance(k, bytes) else k
                v = v.decode() if isinstance(v, bytes) else v
                clean[k] = v

            task_id = key.split(":")[1]
            priority = int(clean.get("priority", 0))
            status = clean.get("status", "pending")

            result.append((task_id, priority, status))

        return result

    # ---------------- DEPENDENCIES ---------------- #

    def add_dependency(self, t1, t2):
        redis_client.rpush("dependencies", f"{str(t1)},{str(t2)}")

    def get_dependencies(self):
        deps = redis_client.lrange("dependencies", 0, -1)

        result = []
        for d in deps:
            d = d.decode() if isinstance(d, bytes) else d

            if "," not in d:
                continue

            t1, t2 = d.split(",", 1)
            result.append((t1.strip(), t2.strip()))

        return result

    # ---------------- STATUS ---------------- #

    def update_status(self, task_id, status):
        task_id = str(task_id)
        redis_client.hset(f"task:{task_id}", "status", str(status))

        # 🔥 broadcast update
        try:
            from app.main import broadcast
            data = self.get_all_status()

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(broadcast(data))
            except RuntimeError:
                asyncio.run(broadcast(data))

        except Exception as e:
            print("Broadcast error:", e)

    def get_status(self, task_id):
        status = redis_client.hget(f"task:{str(task_id)}", "status")
        return status.decode() if isinstance(status, bytes) else status

    def get_all_status(self):
        keys = redis_client.keys("task:*")
        result = {}

        for key in keys:
            key = key.decode() if isinstance(key, bytes) else key
            task_id = key.split(":")[1]

            status = redis_client.hget(key, "status")
            status = status.decode() if isinstance(status, bytes) else status

            result[task_id] = status

        return result

    # ---------------- LOGS ---------------- #

    def add_log(self, task_id, message):
        redis_client.rpush(f"logs:{str(task_id)}", str(message))

    def get_logs(self, task_id):
        logs = redis_client.lrange(f"logs:{str(task_id)}", 0, -1)

        return [
            log.decode() if isinstance(log, bytes) else log
            for log in logs
        ]

    # ---------------- METRICS ---------------- #

    def increment_metric(self, key):
        redis_client.incr(f"metric:{key}")

    def get_metrics(self):
        return {
            "success": int(redis_client.get("metric:success") or 0),
            "failed": int(redis_client.get("metric:failed") or 0)
        }

    # ---------------- CLEANUP ---------------- #

    def clear_all(self):
        # tasks
        for key in redis_client.keys("task:*"):
            redis_client.delete(key)

        # dependencies
        redis_client.delete("dependencies")

        # logs
        for key in redis_client.keys("logs:*"):
            redis_client.delete(key)

        # metrics reset
        redis_client.delete("metric:success")
        redis_client.delete("metric:failed")
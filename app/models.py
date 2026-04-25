from app.redis_client import redis_client

class Database:

    def add_task(self, task_id, priority):
        redis_client.hset(f"task:{task_id}", mapping={
            "priority": priority,
            "status": "pending"
        })

    def add_dependency(self, t1, t2):
        redis_client.rpush("dependencies", f"{t1},{t2}")

    def get_tasks(self):
        keys = redis_client.keys("task:*")
        result = []

        for key in keys:
            data = redis_client.hgetall(key)
            task_id = key.split(":")[1]
            result.append((task_id, int(data["priority"]), data["status"]))

        return result

    def get_dependencies(self):
        deps = redis_client.lrange("dependencies", 0, -1)
        return [tuple(d.split(",")) for d in deps]

    def update_status(self, task_id, status):
        redis_client.hset(f"task:{task_id}", "status", status)

    def get_status(self, task_id):
        return redis_client.hget(f"task:{task_id}", "status")

    def get_all_status(self):
        keys = redis_client.keys("task:*")
        result = {}

        for key in keys:
            task_id = key.split(":")[1]
            status = redis_client.hget(key, "status")
            result[task_id] = status

        return result

    def clear_all(self):
        for key in redis_client.keys("task:*"):
            redis_client.delete(key)
        redis_client.delete("dependencies")
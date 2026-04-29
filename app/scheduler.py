from app.tasks import execute_task
import time
from collections import defaultdict

MAX_PARALLEL = 2   # 🔥 backpressure limit

class Scheduler:
    def __init__(self, db):
        self.db = db
        self.dep_map = defaultdict(list)

    def build_dependency_map(self):
        deps = self.db.get_dependencies()

        print("📌 Dependencies:", deps)

        for parent, child in deps:
            parent = str(parent)
            child = str(child)
            self.dep_map[child].append(parent)

        print("📌 Dependency Map:", dict(self.dep_map))

    def can_run(self, task_id):
        parents = self.dep_map.get(task_id, [])

        for parent in parents:
            if self.db.get_status(parent) != "completed":
                return False

        return True

    def inflight_tasks(self):
        """🔥 count running + queued tasks"""
        statuses = self.db.get_all_status()
        return sum(1 for s in statuses.values() if s in ["queued", "running"])

    def schedule(self):
        print("🚀 Scheduler started...")

        self.build_dependency_map()

        triggered = set()

        while True:
            tasks = self.db.get_tasks()
            all_done = True

            ready = []

            for task_id, priority, _ in tasks:
                task_id = str(task_id)
                status = self.db.get_status(task_id)

                if status != "completed":
                    all_done = False

                if (
                    status == "pending"
                    and task_id not in triggered
                    and self.can_run(task_id)
                ):
                    # 🔥 collect ready tasks
                    ready.append((priority, task_id))

            # 🔥 priority sort (higher priority first)
            ready.sort(reverse=True)

            for _, task_id in ready:

                # 🔥 backpressure check
                if self.inflight_tasks() >= MAX_PARALLEL:
                    break

                print(f"🔥 Running: {task_id}")

                triggered.add(task_id)

                self.db.update_status(task_id, "queued")

                execute_task.delay(task_id)

            if all_done:
                print("✅ All tasks completed")
                break

            time.sleep(1)
from app.dag import DAG
from app.tasks import execute_task

class Scheduler:
    def __init__(self, db):
        self.dag = DAG()
        self.db = db
        self.tasks = {}

    def load(self):
        tasks = self.db.get_tasks()
        deps = self.db.get_dependencies()

        for task_id, priority, status in tasks:
            self.tasks[task_id] = {
                "priority": priority,
                "status": status
            }

        for t1, t2 in deps:
            self.dag.add_edge(t1, t2)

    def schedule(self):
        self.load()

        # ensure all nodes exist
        for task in self.tasks:
            if task not in self.dag.indegree:
                self.dag.indegree[task] = 0

        order = self.dag.topological_sort()

        print("DAG ORDER:", order)

        for task_id in order:
            if self.tasks[task_id]["status"] == "pending":
                
                print(f"Sending task: {task_id}")

                # 🔥 status update → pending → queued
                self.db.update_status(task_id, "queued")

                # 🔥 send to Celery
                execute_task.delay(task_id)
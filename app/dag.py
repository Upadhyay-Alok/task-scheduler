from collections import defaultdict, deque

class DAG:
    def __init__(self):
        self.graph = defaultdict(list)
        self.indegree = {}

    def add_edge(self, u, v):
        # 🔥 HARD FIX: force string हमेशा
        u = str(u)
        v = str(v)

        # 🔥 skip invalid (dict bug guard)
        if isinstance(u, dict) or isinstance(v, dict):
            return

        # graph build
        self.graph[u].append(v)

        # indegree init
        if u not in self.indegree:
            self.indegree[u] = 0

        if v not in self.indegree:
            self.indegree[v] = 0

        # increment
        self.indegree[v] += 1

    def topological_sort(self):
        # 🔥 safe copy
        indegree_copy = {str(k): int(v) for k, v in self.indegree.items()}

        queue = deque()

        # 🔥 safe iteration
        for node in indegree_copy.keys():
            if indegree_copy[node] == 0:
                queue.append(str(node))

        result = []

        while queue:
            node = queue.popleft()
            result.append(str(node))

            # 🔥 safe neighbors
            for neighbor in self.graph.get(node, []):
                neighbor = str(neighbor)

                if neighbor not in indegree_copy:
                    continue

                indegree_copy[neighbor] -= 1

                if indegree_copy[neighbor] == 0:
                    queue.append(neighbor)

        return result
from collections import defaultdict, deque

class DAG:
    def __init__(self):
        self.graph = defaultdict(list)
        self.indegree = defaultdict(int)

    def add_edge(self, u, v):
        self.graph[u].append(v)
        self.indegree[v] += 1
        if u not in self.indegree:
            self.indegree[u] = 0

    def topological_sort(self):
        indegree_copy = dict(self.indegree)

        queue = deque([node for node in indegree_copy if indegree_copy[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            for neighbor in self.graph[node]:
                indegree_copy[neighbor] -= 1
                if indegree_copy[neighbor] == 0:
                    queue.append(neighbor)

        return result
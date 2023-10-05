class Visitor(object):

    def __init__(self, name: str) -> None:
        self.name = name
        self.queues_visited = []

    def __str__(self) -> str:
        return f"name={self.name} visited={self.queues_visited}"

    def visited(self, queue_id: str):
        self.queues_visited.append(queue_id)

    def has_visited(self, queue_id: str):
        for q in self.queues_visited:
            if q == queue_id:
                return True
        return False
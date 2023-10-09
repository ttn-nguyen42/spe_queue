from typing import List, Dict


class VisitorStatistics:
    def __init__(self) -> None:
        self.start_wait_time: float = 0.0
        self.end_wait_time: float = 0.0

    def __str__(self) -> str:
        return f"wait_time={self.get_wait_time()} start_wait_time={self.start_wait_time} end_wait_time={self.end_wait_time}"

    def get_wait_time(self) -> str:
        return self.end_wait_time - self.start_wait_time


class Visitor:

    def __init__(self, name: str) -> None:
        self.name = name
        self.queues_visited: dict[str, VisitorStatistics] = {}

    def __str__(self) -> str:
        return f"name={self.name} visited={self.queues_visited} wait_time={self.get_total_wait_time()} service_time={self.get_total_service_time()}"

    def get_name(self) -> str:
        return self.name

    def visited(self, queue_id: str):
        self.queues_visited[queue_id] = VisitorStatistics(),

    def has_visited(self, queue_id: str):
        res = self.queues_visited.get(queue_id)
        return res is not None

    def get_total_wait_time(self) -> float:
        total: float = 0.0
        for (_, v) in enumerate(self.queues_visited):
            total += v.get_wait_time()
        return total

    def update_wait_time(self, id: str, end: float):
        res = self.queues_visited[id]
        if res is None:
            raise Exception("not exists")
        res.end_wait_time = end
        print(f"STAT: {res}")

    def started_waiting_at(self, id: str) -> float:
        res = self.queues_visited[id]
        if res is None:
            raise Exception("not exists")
        return res.start_wait_time

    def set_wait_start(self, at: float):
        res = self.queues_visited[id]
        if res is None:
            raise Exception("not exists")
        res.start_wait_time = at

    def get_wait_time(self, id: str):
        res = self.queues_visited[id]
        if res is None:
            raise Exception("not exists")
        return res.get_wait_time()

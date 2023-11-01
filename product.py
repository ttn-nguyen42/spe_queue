from typing import List

class ProductStatistics:
    def __init__(self) -> None:
        self.wait_time: float = 0.0
        self.service_time: float = 0.0
        pass

    def set_wait_time(self, t: float):
        self.wait_time = t
        return self

    def set_service_time(self, t: float):
        self.service_time = t
        return self

    def __str__(self) -> str:
        return f"wait_time = {self.wait_time} service_time = {self.service_time}"

    def get_wait_time(self) -> str:
        return self.wait_time

    def get_service_time(self) -> str:
        return self.service_time


class Entry:
    def __init__(self, id: str, stats: ProductStatistics) -> None:
        self.id = id
        self.stats = stats
        pass


class Product:
    def __init__(self, name: str) -> None:
        self.name = name
        self.queues_visited: dict[str, ProductStatistics] = {}

    def __str__(self) -> str:
        return f"name={self.name} visited={self.queues_visited} wait_time={self.get_total_wait_time()} service_time={self.get_total_service_time()}"

    def get_name(self) -> str:
        return self.name

    def visited(self, queue_id: str):
        self.queues_visited[queue_id] = ProductStatistics(),

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

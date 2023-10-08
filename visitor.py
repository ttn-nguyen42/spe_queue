from typing import List


class VisitorStatistics:
    def __init__(self) -> None:
        self.wait_time: float = 0.0
        self.service_time: float = 0.0

        self.start_wait_time: float = 0.0
        self.end_wait_time: float = 0.0
        pass

    def set_wait_time(self, t: float):
        self.wait_time = t

    def set_service_time(self, t: float):
        self.service_time = t

    def __str__(self) -> str:
        return f"wait_time={self.wait_time} service_time={self.service_time} start_wait_time={self.start_wait_time} end_wait_time={self.end_wait_time}"

    def get_wait_time(self) -> str:
        return self.wait_time

    def get_service_time(self) -> str:
        return self.service_time


class Entry:
    def __init__(self, id: str, stats: VisitorStatistics) -> None:
        self.id = id
        self.stats = stats
        pass


class Visitor:

    def __init__(self, name: str) -> None:
        self.name = name
        self.queues_visited: List[Entry] = []

    def __str__(self) -> str:
        return f"name={self.name} visited={self.queues_visited} wait_time={self.get_total_wait_time()} service_time={self.get_total_service_time()}"

    def get_name(self) -> str:
        return self.name

    def visited(self, queue_id: str):
        self.queues_visited.append(
            Entry(id=queue_id, stats=VisitorStatistics()),
        )

    def has_visited(self, queue_id: str):
        for entry in self.queues_visited:
            if entry.id == queue_id:
                return True
        return False

    def get_total_wait_time(self) -> float:
        total: float = 0.0
        for entry in self.queues_visited:
            total += entry.stats.get_wait_time()
        return total

    def get_total_service_time(self) -> float:
        total: float = 0.0
        for entry in self.queues_visited:
            total += entry.stats.get_service_time()
        return total

    def update_wait_time(self, id: str, end: float):
        for r in self.queues_visited:
            if r.id == id:
                r.stats.end_wait_time = end
                r.stats.set_wait_time(end - r.stats.start_wait_time)
                print(f"STAT: {r.stats}")
                return

    def started_waiting_at(self, id: str) -> float:
        for r in self.queues_visited:
            if r.id == id:
                return r.stats.start_wait_time

    def set_wait_start(self, at: float):
        for r in self.queues_visited:
            if r.id == id:
                r.stats.start_wait_time = at
                return

    def get_wait_time(self, id: str):
        for r in self.queues_visited:
            if r.id == id:
                return r.stats.get_wait_time()

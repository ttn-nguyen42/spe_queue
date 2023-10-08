class SystemStatistics:
    def __init__(self, system_name: str) -> None:
        self.system_name = system_name

        self.total_idle_time: float = 0.0

        self.total_service_time: float = 0.0
        self.total_service_requests: int = 0

        self.total_wait_time: float = 0.0
        self.total_visitor_count: int = 0

        self.in_queue_at_end: int = 0
        
        self.utilization: float = 0.0
        pass

    def __str__(self) -> str:
        return f"name={self.system_name} total_idle={self.total_idle_time} avg_service={self.avg_service_time()} avg_wait={self.avg_wait_time()}"

    def avg_service_time(self) -> float:
        if self.total_service_requests == 0:
            return 0.0
        return self.total_service_time / self.total_service_requests

    def avg_wait_time(self) -> float:
        if self.total_visitor_count == 0:
            return 0.0
        return self.total_wait_time / (self.total_visitor_count + self.in_queue_at_end)

    def update_idle_time(self, idle_time: float):
        self.total_idle_time += idle_time
        return

    def set_in_queue_at_end(self, amount: int):
        self.in_queue_at_end = amount

    def update_service_requests(self):
        self.total_service_requests += 1
        return

    def update_service_time(self, service_time: float):
        self.total_service_time += service_time
        return

    def update_visitor_count(self):
        self.total_visitor_count += 1
        return

    def update_wait_time(self, wait_time: float):
        self.total_wait_time += wait_time
        return
        
    def update_utilization(self, avg_servers_usage: float, max_servers: int):
        self.utilization = avg_servers_usage / max_servers * 100
        return
        

    def list_stats(self) -> list:
        stats = []
        stats.append(self.system_name)
        stats.append(round(self.total_idle_time, 5))
        stats.append(round(self.avg_service_time(), 5))
        stats.append(round(self.avg_wait_time(), 5))
        stats.append(self.total_visitor_count)
        stats.append(self.in_queue_at_end)
        stats.append(self.utilization)
        return stats


class EndStats:
    def __init__(self) -> None:
        self.visitor_finished: int = 0
        pass

    def update_visitor_finished(self):
        self.visitor_finished += 1

    def get_visitor_finished(self):
        return self.visitor_finished

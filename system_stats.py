class SystemStatistics:
    def __init__(self, system_name: str) -> None:
        self.system_name = system_name

        self.total_idle_time: float = 0.0
        self.total_idle_count: int = 0

        self.total_service_time: float = 0.0
        self.total_service_requests: int = 0

        self.total_wait_time: float = 0.0
        self.total_visitor_count: int = 0
        pass

    def __str__(self) -> str:
        return f"name={self.system_name} avg_idle={self.avg_idle_time()} avg_service={self.avg_service_time()} avg_wait={self.avg_wait_time()}"

    def avg_idle_time(self) -> float:
        if self.total_idle_count == 0:
            return 0.0
        return self.total_idle_time / self.total_idle_count

    def avg_service_time(self) -> float:
        if self.total_service_requests == 0:
            return 0.0
        return self.total_service_time / self.total_service_requests

    def avg_wait_time(self) -> float:
        if self.total_visitor_count == 0:
            return 0.0
        return self.total_wait_time / self.total_visitor_count
    
    # MMN0208: Update idle time
    def update_idle_count(self):
        self.total_idle_count += 1
        pass
    
    def update_idle_time(self, idle_time: float):
        self.total_idle_time += idle_time
        pass

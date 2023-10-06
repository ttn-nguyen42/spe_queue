class SystemStatistics:
    def __init__(self, system_name: str) -> None:
        self.system_name = system_name

        self.total_idle_time: float = 0.0

        self.total_service_time: float = 0.0
        self.total_service_requests: int = 0

        self.total_wait_time: float = 0.0
        self.total_visitor_count: int = 0
        pass

    def __str__(self) -> str:
        return f"name={self.system_name} total_idle={self.total_idle_time} avg_service={self.avg_service_time()} avg_wait={self.avg_wait_time()}"

    # MMN0208: Use total_idle_time instead
    # def avg_idle_time(self) -> float:
    #     if self.total_idle_count == 0:
    #         return 0.0
    #     return self.total_idle_time / self.total_idle_count

    def avg_service_time(self) -> float:
        if self.total_service_requests == 0:
            return 0.0
        return self.total_service_time / self.total_service_requests

    def avg_wait_time(self) -> float:
        if self.total_visitor_count == 0:
            return 0.0
        return self.total_wait_time / self.total_visitor_count

    # MMN0208: Add update_idle_time function
    def update_idle_time(self, idle_time: float):
        self.total_idle_time += idle_time
        return
    
    # MMN0208: Add update_service_requests and update_service_time functions
    def update_service_requests(self):
        self.total_service_requests += 1
        return
    
    def update_service_time(self, service_time: float):
        self.total_service_time += service_time
        return

    def update_visitor_count(self):
        self.total_visitor_count += 1
        return

    def list_stats(self) -> list:
        stats = []
        stats.append(self.system_name)
        stats.append(self.total_idle_time)
        stats.append(round(self.avg_service_time(), 5))
        stats.append(round(self.avg_wait_time(), 5))
        stats.append(self.total_visitor_count)
        return stats

class SystemStatistics:
    def __init__(self, system_name: str) -> None:
        self.system_name = system_name

        self.total_idle_time: float = 0.0
        self.total_idle_count: int = 0.0

        self.total_service_time: float = 0.0
        self.total_service_requests: int = 0
        pass

    def __str__(self) -> str:
        return f"name={self.system_name} avg_idle={self.avg_idle_time()} avg_service={self.avg_service_time()}"

    def avg_idle_time(self) -> float:
        return self.total_idle_time / self.total_idle_count

    def avg_service_time(self) -> float:
        return self.total_service_time / self.total_service_requests

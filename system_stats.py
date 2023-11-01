import params as pr

class SystemStatistics:
    def __init__(self, system_name: str) -> None:
        self.system_name = system_name

        self.total_idle_time: float = 0.0

        self.total_interarrival_time: float = 0.0
        
        self.total_service_time: float = 0.0
        self.total_service_requests: int = 0

        self.total_wait_time: float = 0.0
        self.total_product_count: int = 0
        
        self.utilization: float = 0.0
        self.total_product_count: int = 0
        self.in_queue_at_end: int = 0
        pass

    def __str__(self) -> str:
        return f"name={self.system_name} total_idle={self.total_idle_time} avg_service={self.avg_service_time()} avg_wait={self.avg_wait_time()}"

    def avg_service_time(self) -> float:
        if self.total_service_requests == 0:
            return 0.0
        return self.total_service_time / self.total_service_requests
    
    def avg_interarrival_time(self) -> float:
        if self.total_product_count == 0:
            return 0.0
        return self.total_interarrival_time / (self.total_product_count + self.in_queue_at_end)

    def avg_wait_time(self) -> float:
        if self.total_product_count == 0:
            return 0.0
        return self.total_wait_time / (self.total_product_count + self.in_queue_at_end)

    def update_idle_time(self, idle_time: float):
        self.total_idle_time += idle_time
        return

    def set_in_queue_at_end(self, amount: int):
        self.in_queue_at_end = amount

    def update_total_interarrival_time(self, interarrival_time: float):
        self.total_interarrival_time += interarrival_time
        return
    
    def update_service_requests(self):
        self.total_service_requests += 1
        return

    def update_service_time(self, service_time: float):
        self.total_service_time += service_time
        return

    def update_product_count(self):
        self.total_product_count += 1
        return

    def update_wait_time(self, wait_time: float):
        self.total_wait_time += wait_time
        return

    def update_utilization(self, max_servers: int):
        self.utilization = self.arrival_rate() / (max_servers * self.service_rate())
        return
    
    def get_avg_in_sys(self):
        return self.utilization / (1 - self.utilization)
    
    def get_avg_in_queue(self):
        return  self.utilization / (1 - self.utilization) - self.utilization
    
    def arrival_rate(self) -> float:
        return 3600 / self.avg_interarrival_time()
    
    def service_rate(self) -> float:
        return 3600 / self.avg_service_time()

    def list_stats(self) -> list:
        stats = []
        stats.append(self.system_name)
        stats.append(str(round(self.arrival_rate(), 4)))
        stats.append(str(round(self.service_rate(), 4)))
        stats.append(str(round(self.utilization, 4)))
        stats.append(round(self.get_avg_in_sys(), 4))
        stats.append(round(self.get_avg_in_queue(), 4))
        stats.append(self.total_product_count)
        stats.append(self.in_queue_at_end)
        return stats

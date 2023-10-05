SIM_DURATION = 20


class ServerParams(object):
    def __init__(
        self,
        mean_service_time: int,
    ) -> None:
        self.mean_service_time = mean_service_time


class QueueParams(object):
    def __init__(
        self,
        max_queue_size: int,
    ) -> None:
        self.max_queue_size = max_queue_size
        pass


class GeneratorParams(object):
    def __init__(
            self,
            num_rooms: int,
            mean_interarrival_time: int,
    ) -> None:
        self.num_rooms = num_rooms
        self.mean_interarrival_time = mean_interarrival_time
        pass


class SystemParams(object):
    def __init__(
        self,
        name: str,
        max_servers: int,
    ) -> None:
        self.name = name
        self.max_servers = max_servers
        pass

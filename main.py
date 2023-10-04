import simpy as sp
import numpy as np
from typing import List

SIM_DURATION = 20


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


class VisitorServer:
    """
    Process visitor
    """

    def __init__(self) -> None:
        pass

    def process(self, visitor: Visitor):
        pass

    def stop(self):
        pass


class Queue:
    """
    Hold visitors
    """

    def __init__(
        self,
        params: QueueParams,
    ) -> None:
        self.visitors: List[Visitor] = []
        self.params = params
        return

    def enqueue(self, visitor: Visitor):
        if self.is_full():
            raise Exception("queue is full")
        self.visitors.append(visitor)

    def dequeue(self) -> Visitor:
        if self.is_empty():
            raise Exception("queue is empty")
        return self.visitors.pop(0)

    def is_empty(self):
        return len(self.visitors) == 0

    def is_full(self):
        return len(self.visitors) >= self.params.max_queue_size

    def __len__(self):
        return len(self.visitors)

    def capacity(self):
        return self.params.max_queue_size


class System:
    """
    Manages a queue and its servers
    """

    def __init__(
        self,
        env: sp.Environment,
        params: SystemParams,
        queue_params: QueueParams,
        server_params: ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        self.server_params = server_params
        self.queue = Queue(params=queue_params)
        self.available_servers = sp.Resource(
            self.env, capacity=params.max_servers)
        pass

    def add_visitor(self, visitor: Visitor):
        self.queue.enqueue(visitor=visitor)

    def find_visitor(self) -> Visitor:
        try:
            return self.queue.dequeue()
        except Exception:
            return None

    def serve(self, visitor: Visitor):
        pass

    def schedule(self):
        pass


class ReceptionServer(VisitorServer):
    def __init__(self, env: sp.Environment, params: ServerParams) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, visitor: Visitor):
        print(f"ReceptionServer received visitor {visitor.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time))
        print(
            f"ReceptionServer process paper work for {visitor.name} in {service_time}")
        yield self.env.timeout(service_time)
        print(f"ReceptionServer process done for {visitor.name}")

    def stop(self):
        return


class Reception(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams
    ) -> None:
        super().__init__(env, params, queue_params, server_params)

    def serve(self, visitor: Visitor, req: sp.Resource):
        server = ReceptionServer(
            env=self.env,
            params=self.server_params,
        )
        yield from server.process(visitor=visitor)
        self.available_servers.release(request=req)
        

    def add_visitor(self, visitor: Visitor):
        self.queue.enqueue(visitor=visitor)
        if not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    def schedule(self):
        while True:
            if self.queue.is_empty():
                # None when queue is empty
                idle_timeout = self._idle()
                self.idle_proc = self.env.process(idle_timeout)
                yield self.idle_proc
            else:
                count = self.available_servers.count
                cap = self.available_servers.capacity
                if count < cap:
                    req = self.available_servers.request()
                    visitor = self.find_visitor()
                    yield req
                    yield self.env.process(self.serve(visitor=visitor, req=req))
                else:
                    print("No server available")

    def _idle(self):
        try:
            print(f"Reception is idling at {self.env.now}")
            yield self.env.timeout(SIM_DURATION)
        except sp.Interrupt:
            print(f"Reception now working")

    def _run_idle(self):
        idle_timeout = self._idle()
        self.idle_proc = self.env.process(idle_timeout)
        yield self.idle_proc

    def run(self):
        self.env.process(self.schedule())


class Generator:
    def __init__(
        self,
        env: sp.Environment,
        params: GeneratorParams,
        reception: System,
    ) -> None:
        self.env = env
        self.params = params
        self.reception = reception

    def generate(self):
        while True:
            interarrival = np.random.exponential(
                self.params.mean_interarrival_time)
            yield self.env.timeout(interarrival)
            print(f"Message sent at {self.env.now}")
            self.reception.add_visitor(visitor=Visitor(name="ABC"))

    def run(self):
        self.env.process(self.generate())


if __name__ == "__main__":
    env = sp.Environment()

    reception = Reception(
        env=env,
        params=SystemParams(name="Reception", max_servers=3),
        queue_params=QueueParams(max_queue_size=2000),
        server_params=ServerParams(mean_service_time=3)
    )

    gen = Generator(
        env=env,
        params=GeneratorParams(
            num_rooms=1,
            mean_interarrival_time=1
        ),
        reception=reception,
    )

    reception.run()
    gen.run()
    env.run(until=SIM_DURATION)

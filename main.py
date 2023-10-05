import simpy as sp
import numpy as np
import params as pr
from visitor import Visitor
from visitor_queue import Queue
from servers import ReceptionServer

SIM_DURATION = 20


class System:
    """
    Manages a queue and its servers
    """

    def __init__(
        self,
        env: sp.Environment,
        params: pr.SystemParams,
        queue_params: pr.QueueParams,
        server_params: pr.ServerParams,
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


class Reception(System):
    def __init__(
            self,
            env: sp.Environment,
            params: pr.SystemParams,
            queue_params: pr.QueueParams,
            server_params: pr.ServerParams
    ) -> None:
        super().__init__(env, params, queue_params, server_params)

    def serve(self, visitor: Visitor, req: sp.Resource):
        server = ReceptionServer(
            env=self.env,
            params=self.server_params,
        )
        yield from server.process(visitor=visitor)
        self.available_servers.release(request=req)
        if not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    def add_visitor(self, visitor: Visitor):
        self.queue.enqueue(visitor=visitor)
        if not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    def schedule(self):
        while True:
            # There's a message
            if not self.queue.is_empty():
                count = self.available_servers.count
                cap = self.available_servers.capacity
                if count < cap:
                    # There's a server
                    req = self.available_servers.request()
                    visitor = self.find_visitor()
                    yield req
                    self.env.process(self.serve(visitor=visitor, req=req))
                    continue
            print("No message or servers available, go idle")
            idle_timeout = self._idle()
            self.idle_proc = self.env.process(idle_timeout)
            yield self.idle_proc

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
        params: pr.GeneratorParams,
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
        params=pr.SystemParams(name="Reception", max_servers=3),
        queue_params=pr.QueueParams(max_queue_size=2000),
        server_params=pr.ServerParams(mean_service_time=3)
    )

    gen = Generator(
        env=env,
        params=pr.GeneratorParams(
            num_rooms=1,
            mean_interarrival_time=1
        ),
        reception=reception,
    )

    reception.run()
    gen.run()
    env.run(until=SIM_DURATION)

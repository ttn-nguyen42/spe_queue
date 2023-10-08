import simpy as sp
import params as pr
from visitor import Visitor
from qs import Queue
from system_stats import SystemStatistics


class System:

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
        self.stats = SystemStatistics(system_name=self.params.name)

    def get_stats(self) -> SystemStatistics:
        return self.stats

    def add_visitor(self, visitor: Visitor):
        self.queue.enqueue(visitor=visitor)

    def find_visitor(self) -> Visitor:
        try:
            return self.queue.dequeue()
        except Exception:
            return None

    def is_empty(self) -> bool:
        return self.queue.is_empty()

    def is_full(self) -> bool:
        return self.queue.is_full()

    def is_available(self) -> bool:
        cap = self.available_servers.capacity
        in_use = self.available_servers.count
        return in_use < cap

    def is_active(self) -> bool:
        return self.available_servers.count > 0

    def serve(self, visitor: Visitor, req: sp.Resource):
        pass

    def schedule(self):
        pass

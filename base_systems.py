import simpy as sp
import numpy as np
import params as pr
from visitor import Visitor, Entry, VisitorStatistics
from servers import VisitorServer
from qs import Queue
from system_stats import SystemStatistics
from simpy.resources.resource import Request


class SystemScheduleResult:
    FOUND_VISITOR = 1,
    NO_VISITOR = 2,
    NO_SERVER = 3,


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
        self.active_proc = None
        self.idle_proc = None
        self.is_idle = True

        # MMN0208: server utilization
        self.servers_usage = []

    def get_stats(self) -> SystemStatistics:
        return self.stats

    # MMN0208: server utilization
    def _monitor_servers(self):
        while True:
            self.servers_usage.append(self.available_servers.count)
            yield self.env.timeout(0.25)

    def get_name(self) -> str:
        return self.params.name

    def add_visitor(self, visitor: Visitor):
        self.queue.enqueue(visitor=visitor)

        stats = VisitorStatistics()
        ent = Entry(
            id=self.get_name(),
            stats=stats,
        )
        stats.start_wait_time = self.env.now

        visitor.queues_visited.append(ent)

        if self.is_idle:
            self._stop_idle()

        if self.is_available():
            self._stop_active()

    def _get_visitor(self) -> Visitor:
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

    def _stop_idle(self):
        self.is_idle = False
        if self.idle_proc is not None and not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    def _stop_active(self):
        if self.active_proc is not None and not self.active_proc.triggered:
            self.active_proc.interrupt()

    def _active(self):
        try:
            active_start = self.env.now
            print(
                f"At time t = {active_start}, {self.get_name()} ACTIVE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            active_end = self.env.now
            print(
                f"At time t = {active_end}, {self.get_name()} ACTIVE ends")

    def _idle(self):
        try:
            idle_start = self.env.now
            print(f"At time t = {idle_start}, {self.get_name()} IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            idle_end = self.env.now
            print(f"At time t = {idle_end}, {self.get_name()} IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _calculate_in_queue_wait_time(self):
        remaining_visitors = self.queue.visitors
        self.stats.in_queue_at_end = len(remaining_visitors)
        for v in remaining_visitors:
            v.update_wait_time(id=self.get_name(), end=self.env.now)
            self.stats.update_wait_time(
                wait_time=v.get_wait_time(id=self.get_name()))

    def go_active(self) -> sp.Process:
        active_state = self._active()
        self.active_proc = self.env.process(active_state)
        yield self.active_proc

    def go_idle(self) -> sp.Process:
        self.is_idle = True
        idle_timeout = self._idle()
        self.idle_proc = self.env.process(idle_timeout)
        yield self.idle_proc

    def request_server(self) -> (SystemScheduleResult, Visitor, Request):
        if not self.is_empty():
            if self.is_available():
                req = self.available_servers.request()
                print(
                    f"{self.get_name()} servers count = {self.available_servers.count}/{self.available_servers.capacity}")
                visitor = self._get_visitor()
                self._schedule_update_stats(visitor=visitor)
                return SystemScheduleResult.FOUND_VISITOR, visitor, req
            else:
                return SystemScheduleResult.NO_SERVER, None, None
        else:
            print(
                f"At time t = {self.env.now}, {self.get_name()} NO_VISITOR idle start")
            return SystemScheduleResult.NO_VISITOR, None, None

    def serve(self, visitor: Visitor, req: sp.Resource, server: VisitorServer) -> sp.Event:
        service_start = self.env.now
        yield from server.process(visitor=visitor)
        service_end = self.env.now
        self.stats.update_service_time(service_end - service_start)

        self.available_servers.release(request=req)
        if self.is_available():
            self._stop_active()

    def _schedule_update_stats(self, visitor: Visitor):
        self.stats.update_service_requests()
        self.stats.update_visitor_count()

        visitor.update_wait_time(
            id=self.get_name(),
            end=self.env.now)

        self.stats.update_wait_time(
            wait_time=visitor.get_wait_time(id=self.get_name()))

    def schedule(self):
        pass

    def run(self):
        # MMN0208: server utilization
        self.env.process(self._monitor_servers())
        pass

    def stop(self):
        self._stop_idle()
        self._stop_active()
        self._calculate_in_queue_wait_time()
        self.stats.update_utilization(
            np.mean(self.servers_usage), self.params.max_servers)

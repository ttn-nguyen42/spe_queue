import simpy as sp
from params import ServerParams, SystemParams, SIM_DURATION
from product import Product, ProductStatistics
from servers import  ProductServer
from qs import Queue
from system_stats import SystemStatistics
from simpy.resources.resource import Request
from typing import Tuple


class SystemScheduleResult:
    FOUND_PRODUCT = 1,
    NO_PRODUCT = 2,
    NO_SERVER = 3,


class System:
    def __init__(
        self,
        env: sp.Environment,
        params: SystemParams,
        server_params: ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        self.server_params = server_params
        self.queue = Queue()
        self.available_servers = sp.Resource(
            self.env, capacity=params.max_servers)
        self.stats = SystemStatistics(system_name=self.params.name)
        self.active_proc = None
        self.idle_proc = None
        self.is_idle = True
        self.prev_arrival = 0.0

        # MMN0208: server utilization
        self.servers_usage = []
        self.queue_length = []
        self.current_in_sys = []

    def get_stats(self) -> SystemStatistics:
        return self.stats

    # MMN0208: server utilization
    def _monitor(self):
        while True:
            self.servers_usage.append(self.available_servers.count)
            self.queue_length.append(self.queue.__len__())
            yield self.env.timeout(0.25)

    def get_name(self) -> str:
        return self.params.name

    def add_product(self, product: Product):
        self.queue.enqueue(product=product)
        
        self.stats.update_total_interarrival_time(
            interarrival_time=self.env.now - self.prev_arrival)
        self.prev_arrival = self.env.now

        stats = ProductStatistics()
        stats.start_wait_time = self.env.now

        product.queues_visited[self.get_name()] = stats

        if self.is_idle:
            self._stop_idle()

        if self.is_available():
            self._stop_active()

    def _get_product(self) -> Product:
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

    def __len__(self) -> int:
        return len(self.queue)

    
    def availability(self, args = None) -> Tuple[float, float]:
        server_ratio = 0.0
        if self.available_servers.capacity == 0:
            server_ratio = 0.0
        else:
            server_ratio = self.available_servers.count / self.available_servers.capacity
        queue_ratio = 0.0
        if self.queue.capacity == 0:
            queue_ratio = 0.0
        else:
            queue_ratio = len(self.queue) / self.queue.capacity()
        return (server_ratio, queue_ratio)

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
            # print(
            #     f"At time t = {active_start}, {self.get_name()} ACTIVE starts")

            yield self.env.timeout(SIM_DURATION)
        except sp.Interrupt:
            active_end = self.env.now
            # print(
            #     f"At time t = {active_end}, {self.get_name()} ACTIVE ends")

    def _idle(self):
        try:
            idle_start = self.env.now
            # print(f"At time t = {idle_start}, {self.get_name()} IDLE starts")
            yield self.env.timeout(SIM_DURATION)
        except sp.Interrupt:
            idle_end = self.env.now
            # print(f"At time t = {idle_end}, {self.get_name()} IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _calculate_in_queue_wait_time(self):
        remaining_products = self.queue.products
        self.stats.in_queue_at_end = len(remaining_products)
        for v in remaining_products:
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

    def request_server(self) -> (SystemScheduleResult, Product, Request):
        if not self.is_empty():
            if self.is_available():
                req = self.available_servers.request()
                # print(
                #     f"{self.get_name()} servers count = {self.available_servers.count}/{self.available_servers.capacity}")
                product = self._get_product()
                self._schedule_update_stats(product=product)
                return SystemScheduleResult.FOUND_PRODUCT, product, req
            else:
                return SystemScheduleResult.NO_PRODUCT, None, None
        else:
            # print(
            #     f"At time t = {self.env.now}, {self.get_name()} NO_SERVER idle start")
            return SystemScheduleResult.NO_SERVER, None, None

    def serve(self, product: Product, req: sp.Resource, server: ProductServer) -> sp.Event:
        service_start = self.env.now
        yield from server.process(product=product)
        service_end = self.env.now
        self.stats.update_service_time(service_end - service_start)

        self.available_servers.release(request=req)
        if self.is_available():
            self._stop_active()

    def _schedule_update_stats(self, product: Product):
        self.stats.update_service_requests()
        self.stats.update_product_count()

        product.update_wait_time(
            id=self.get_name(),
            end=self.env.now)

        self.stats.update_wait_time(
            wait_time=product.get_wait_time(id=self.get_name()))

    def schedule(self):
        pass

    def run(self):
        # MMN0208: server utilization
        self.env.process(self._monitor())
        pass

    def stop(self):
        self._stop_idle()
        self._stop_active()
        self._calculate_in_queue_wait_time()
        self.stats.update_utilization(self.params.max_servers)
import simpy as sp
import numpy as np
import params as pr
from product import Product
from qs import Queue
from params import ServerParams, QueueParams, SystemParams
from servers import ProductionLineServer, DispatcherServer, ProductServer
from system_stats import SystemStatistics
import random
from base_systems import System, SystemScheduleResult
from numpy.random import choice

class ProductionLine(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_lines: System = None) -> None:
        self.production_lines = production_lines
        # self.env = env
        # self.params = params
        # self.queue_params = queue_params
        # self.server_params = server_params
        super().__init__(env, params=params, queue_params=queue_params, server_params=server_params)
                
    def schedule(self):
        while True:
            res, product, req = self.request_server() 
            match res:
                case SystemScheduleResult.FOUND_PRODUCT:
                    server = ProductionLineServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        product=product, req=req, server=server))
                    self._move_to_next_qa_line(product=product)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()  

    def _move_to_next_qa_line(self, product: Product):
        # next_lines = np.random.choice(np.array(all_lines)[:3], 1, p=[0.5, 0.4, 0.1])
        # next_lines[0].add_product(product=product) 
        return
    
    def run(self):
        super().run()
        self.env.process(self.schedule())

class Dispatcher(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_lines: list[ProductionLine] = None) -> None:
        self.production_lines = production_lines
        super().__init__(env, params, queue_params, server_params)

    def set_production_lines(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self
    

    def schedule(self):
        while True:
            res, product, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_PRODUCT:
                    server = DispatcherServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        product=product, req=req, server=server))
                    self._move_to_next_production_line(product=product)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    def _move_to_next_production_line(self, product: Product):
        print(
            f"At time t = {self.env.now}, Dispatcher MOVE_TO_PRODUCTION_LINE product = {product.get_name()}")
        all_lines = self.production_lines
        if self.production_lines is None:
            return
        
        next_lines = np.random.choice(np.array(all_lines)[:3], 1, p=[0.5, 0.4, 0.1])
        next_lines[0].add_product(product=product)
        
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

class QACheck(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_lines: list[ProductionLine]) -> None:    
        self.production_lines = production_lines
        super().__init__(env, params, queue_params, server_params)

    def set_production_lines(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self


    def schedule(self):
        print("DEF", self.production_lines)
        while True:
            res, product, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_PRODUCT:
                    server = QACheckServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        product=product, req=req, server=server))
                    self._move_to_next_production_line(product=product)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    def _move_to_next_production_line(self, product: Product):
        print(
            f"At time t = {self.env.now}, QACheck MOVE_TO_PRODUCTION_LINE product = {product.get_name()}")
        all_lines: list[System] = []
        if self.production_lines is None:
            return

        for line in enumerate(self.production_lines):
            all_lines.append(line)
        
        next_lines = np.random.choice(np.array(all_lines)[:3], 3, p=[0.5, 0.4, 0.1])
        all_lines[0].add_product(product=product)
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

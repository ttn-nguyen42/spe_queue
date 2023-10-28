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
            server_params: ServerParams) -> None:
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
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

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
            production_line: list[ProductionLine] = None) -> None:
        self.production_line = production_line
        super().__init__(env, params, queue_params, server_params)

    def set_production_line(self, production_lines: list[ProductionLine]):
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
        production_line =["production_line_a", "production_line_b", "advanced_prod_line"]
        product = np.random.choice(production_line, 3, p=[0.5, 0.4, 0.1])
        production_line.add_product(product=product)

        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

# class ProductionLine(System):
#     def __init__(
#         self,
#         env: sp.Environment,
#         name: str,
#         queue_params: pr.QueueParams,
#         server_params: pr.ServerParams,
#     ) -> None:
#         super().__init__(env, name, queue_params, server_params)

#     def schedule(self):
#         while True:
#             product, request = self.request_server()
#             if product is not None:
#                 if self.qa_check is not None:
#                     self.qa_check.add_product(product=product)
#                 else:
#                     product.is_complete = True

#                 self.server.release(request)

#             else:
#                 yield self.env.timeout(0.25)

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
        product = np.random.choice(len(production_line), 5, p=[0.6, 0.4])
        production_line.add_product(product=product)
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

import simpy as sp
import numpy as np
import params as pr
from product import Product
from qs import Queue
from params import ServerParams, QueueParams, SystemParams
from servers import ProductionLineServer, DispatcherServer, ProductServer, QACheckServer
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
            qa_check: System) -> None:
        self.qa_check = qa_check
        super().__init__(env, params=params,
                         queue_params=queue_params, server_params=server_params)

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
                    self._move_to_next_production_line(product=product)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    def _move_to_next_production_line(self, product: Product):

        if self.qa_check != None:
            self.qa_check.add_product(product=product)
            print(
                f"At time t = {self.env.now}, ProductionLine MOVE_TO_CHECK_LINE productionline = {product.get_name()} qa_check={self.qa_check.get_name()}")
        else:
            print(
                f"At time t = {self.env.now}, ProductionLine MOVE_TO_CHECK_LINE productionline = {product.get_name()} straight to exit")
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

    # def set_production_lines(self, production_lines: list[ProductionLine]):
    #     self.production_lines = production_lines
    #     return self

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
        else:
            next_lines = np.random.choice(
                np.array(all_lines[:3]), 3, p=[0.5, 0.4, 0.1])
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
        all_lines = self.production_lines
        if self.production_lines is None:
            return

        next_lines = np.random.choice(np.array(all_lines[:2]), 2, p=[0.6, 0.4])
        next_lines[0].add_product(product=product)
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

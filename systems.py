import simpy as sp
import params as pr
from product import Product
from qs import Queue
from servers import ProductionLineServer, DispatcherServer
from system_stats import SystemStatistics
# import random
from base_systems import System, SystemScheduleResult
from numpy.random import choice

class Product:
    def __init__(self, name: str, processing_time: float):
        self.name = name
        self.processing_time = processing_time

    def get_name(self) -> str:
        return self.name

    def get_processing_time(self) -> float:
        return self.processing_time

class Dispatcher(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_line: ProductionLine = None) -> None:
        self.production_lines = production_lines
        line_prob = [0.5,0.4,0.1]
        super().__init__(env, params, queue_params, server_params)

    def set_production_line(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self
    

    def schedule(self):
        while True:
            res, product, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_SERVER:
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
            f"At time t = {self.env.now}, Reception MOVE_TO_ROOM visitor = {product.get_name()}")
        
            product = np.random.choice(len(production_line), 5, p=[0.5, 0.4, 0.1])
            production_line.add_product(product=product)
            return

        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

class ProductionLine(System):
    def __init__(
        self,
        env: sp.Environment,
        name: str,
        queue_params: pr.QueueParams,
        server_params: pr.ServerParams,
        qa_check: QACheck = None, 
    ) -> None:
        super().__init__(env, name, queue_params, server_params)
        self.qa_check = qa_check

    def schedule(self):
        while True:
            visitor, request = self.request_server()
            if visitor is not None:
                if self.qa_check is not None:
                    self.qa_check.add_visitor(visitor=visitor)
                else:
                    visitor.is_complete = True

                self.server.release(request)

            else:
                yield self.env.timeout(0.25)

class QACheck(System):
    def __init__(
            self,
            env: simpy.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_lines: list[ProductionLine],
            hallway: System = None) -> None:    
        self.production_lines = production_lines
        super().__init__(env, params, queue_params, server_params)
        line_prob = [0.6,0.4]

    def set_production_lines(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self


    def schedule(self):
        while True:
            res, product, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_SERVER:
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

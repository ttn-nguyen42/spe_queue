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


class Destination:
    def __init__(
        self,
        name: str,
        probability: float,
        system: System,
    ) -> None:
        self.name = name
        self.probability = probability
        self.system = system
        pass


class ProductionLine(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            qa_check: list[Destination]) -> None:
        self.qa_check_destinations = qa_check
        self.probabilties = []
        for destination in self.qa_check_destinations:
            self.probabilties.append(destination.probability)
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
        # a production line either moves the product to the end, or another QA line
        if len(self.qa_check_destinations) == 0:
            print(
                f"t = {self.env.now}, ProductionLine line = {self.get_name()} MOVE_TO_CHECK_LINE product = {product.get_name()} STRAIGHT TO EXIT")
            return

        probabilities = self.probabilties
        next_lines = np.random.choice(
            self.qa_check_destinations, 1, p=probabilities)
        next_line = next_lines[0]

        # if got destination of exit, do nothing
        if next_line.name == "exit":
            print(
                f"t = {self.env.now}, ProductionLine line = {self.get_name()} MOVE_TO_CHECK_LINE product = {product.get_name()} EXIT probability = {next_line.probability}")
            return

        next_line.system.add_product(product=product)
        print(
            f"t = {self.env.now}, ProductionLine line = {self.get_name()} MOVE_TO_CHECK_LINE product = {product.get_name()} qa_check={next_line.name} probability = {next_line.probability}")

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
            production_lines: list[Destination]) -> None:
        self.production_lines = production_lines
        self.line_probabilities = []
        for line in production_lines:
            self.line_probabilities.append(line.probability)

        super().__init__(env, params, queue_params, server_params)

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

        if (self.production_lines is None) or (len(self.production_lines) == 0):
            print(f"Dispatcher have no production lines, this must not happens")
            exit(10)
        else:
            next_lines = np.random.choice(
                self.production_lines, 1, p=self.line_probabilities)
            next_line = next_lines[0]

            next_line.system.add_product(product=product)
            print(
                f"t = {self.env.now}, Dispatcher MOVE_TO_PRODUCTION_LINE line = {next_line.name} probability = {next_line.probability} product = {product.get_name()}")

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
            go_to: list[Destination]) -> None:
        self.production_lines_destinations = go_to
        self.probabilities = []
        for line in self.production_lines_destinations:
            self.probabilities.append(line.probability)
        super().__init__(env, params, queue_params, server_params)

    def set_production_lines(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self

    def set_product_lines_destinations(self, destinations: list[Destination]):
        self.production_lines_destinations = destinations

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
        if len(self.production_lines_destinations) == 0:
            print(
                f"t = {self.env.now}, QACheck check = {self.get_name()} MOVE_TO_PRODUCTION_LINE product = {product.get_name()} STRAIGHT TO EXIT")
            return

        next_lines = np.random.choice(
            self.production_lines_destinations, 1, p=self.probabilities)
        next_line = next_lines[0]

        # if got destination of exit, do nothing
        if next_line.name == "exit":
            print(
                f"t = {self.env.now}, QACheck check = {self.get_name()} MOVE_TO_PRODUCTION_LINE product = {product.get_name()} EXIST probability = {next_line.probability}")
            return

        next_line.system.add_product(product=product)
        print(
            f"t = {self.env.now}, QACheck check = {self.get_name()} MOVE_TO_PRODUCTION_LINE product = {product.get_name()} production_line = {next_line.name} probability = {next_line.probability}")

    def run(self):
        super().run()
        self.env.process(self.schedule())

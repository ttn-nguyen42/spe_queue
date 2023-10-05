from visitor import Visitor
import simpy as sp
import params as pr
import numpy as np


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


class ReceptionServer(VisitorServer):
    def __init__(self, env: sp.Environment, params: pr.ServerParams) -> None:
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

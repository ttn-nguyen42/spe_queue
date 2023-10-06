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
        print(f"At time t = {self.env.now}, ReceptionServer RECEIVE visitor = {visitor.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time))
        print(
            f"At time t = {self.env.now}, ReceptionServer START visitor = {visitor.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(f"At time t = {self.env.now}, ReceptionServer FINISH visitor = {visitor.name}")

    def stop(self):
        return


class RoomServer(VisitorServer):
    def __init__(
        self,
        env: sp.Environment,
        params: pr.ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, visitor: Visitor):
        print(f"At time t = {self.env.now}, RoomServer RECEIVE visitor = {visitor.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time,
        ))
        print(f"At time t = {self.env.now}, RoomServer START visitor = {visitor.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(f"At time t = {self.env.now}, RoomServer FINISH visitor = {visitor.name}")

    def stop(self):
        return

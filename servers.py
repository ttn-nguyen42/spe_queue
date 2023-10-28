from visitor import Visitor
import simpy as sp
import params as pr
import numpy as np
import systems as st

class Server:
    def __init__(self, env, mean_service_time, name):
        self.env = env
        self.mean_service_time = mean_service_time
        self.name = name
        self.mean_service_time = mean_service_time
        self.name = name

    def process(self, job):
        service_time = np.random.exponential(self.mean_service_time)
    def process(self, job):
        service_time = np.random.exponential(self.mean_service_time)
        yield self.env.timeout(service_time)
        print(f"At time t = {self.env.now}, Server {self.name}: Job {job.name} processed in {service_time} time.")

class ProductionLineServer(Server):
    def __init__(
        self,
        env: sp.Environment,
        params: pr.ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, product: product):
        print(
            f"At time t = {self.env.now}, RoomServer RECEIVE product = {product.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time,
        ))
        print(
            f"At time t = {self.env.now}, RoomServer START product = {product.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(
            f"At time t = {self.env.now}, RoomServer FINISH product = {product.name}")

    def stop(self):
        return  
        
class DispatcherServer(Server):
     def __init__(self, env: sp.Environment, params: pr.ServerParams) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, productor: Product):
        print(
            f"At time t = {self.env.now}, ReceptionServer RECEIVE product = {product.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time))
        print(
            f"At time t = {self.env.now}, ReceptionServer START product = {product.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(
            f"At time t = {self.env.now}, ReceptionServer FINISH product = {product.name}")

    def stop(self):
        return


# class VisitorServer:
#     """
#     Process visitor
#     """

#     def __init__(self) -> None:
#         pass

#     def process(self, visitor: Visitor) -> sp.Event:
#         pass

#     def stop(self):
#         pass
    

# class ReceptionServer(VisitorServer):
#     def __init__(self, env: sp.Environment, params: pr.ServerParams) -> None:
#         self.env = env
#         self.params = params
#         super().__init__()

#     def process(self, visitor: Visitor):
#         print(
#             f"At time t = {self.env.now}, ReceptionServer RECEIVE visitor = {visitor.name}")
#         service_time = max(1, np.random.exponential(
#             self.params.mean_service_time))
#         print(
#             f"At time t = {self.env.now}, ReceptionServer START visitor = {visitor.name}, duration = {service_time}")
#         yield self.env.timeout(service_time)
#         print(
#             f"At time t = {self.env.now}, ReceptionServer FINISH visitor = {visitor.name}")

#     def stop(self):
#         return


# class RoomServer(VisitorServer):
#     def __init__(
#         self,
#         env: sp.Environment,
#         params: pr.ServerParams,
#     ) -> None:
#         self.env = env
#         self.params = params
#         super().__init__()

#     def process(self, visitor: Visitor):
#         print(
#             f"At time t = {self.env.now}, RoomServer RECEIVE visitor = {visitor.name}")
#         service_time = max(1, np.random.exponential(
#             self.params.mean_service_time,
#         ))
#         print(
#             f"At time t = {self.env.now}, RoomServer START visitor = {visitor.name}, duration = {service_time}")
#         yield self.env.timeout(service_time)
#         print(
#             f"At time t = {self.env.now}, RoomServer FINISH visitor = {visitor.name}")

#     def stop(self):
#         return


# class HallwayServer(VisitorServer):
#     def __init__(
#         self,
#         env: sp.Environment,
#         params: pr.ServerParams,
#     ) -> None:
#         self.env = env
#         self.params = params
#         super().__init__()

#     def process(self, visitor: Visitor):
#         print(
#             f"At time t = {self.env.now}, HallwayServer RECEIVE visitor = {visitor.name}")
#         service_time = max(1, np.random.exponential(
#             self.params.mean_service_time,
#         ))
#         print(
#             f"At time t = {self.env.now}, HallwayServer START visitor = {visitor.name}, duration = {service_time}")
#         yield self.env.timeout(service_time)
#         print(
#             f"At time t = {self.env.now}, HallwayServer FINISH visitor = {visitor.name}")

#     def stop(self):
#         return

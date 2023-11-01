from product import Product
import simpy as sp
import params as pr
import numpy as np
import systems as st

class ProductServer:
    def __init__(self) -> None:
        pass

    def process(self, product: Product) -> sp.Event:
        pass
    
    def stop(self):
        pass

class ProductionLineServer(ProductServer):
    def __init__(
        self,
        env: sp.Environment,
        params: pr.ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, product: Product):
        # print(
        #     f"At time t = {self.env.now}, ProductionLineServer RECEIVE product = {product.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time,
        ))
        # print(
        #     f"At time t = {self.env.now}, ProductionLineServer START product = {product.name}, duration = {service_time}")
        yield self.env.timeout(service_time)

    def stop(self):
        return  
        
class QACheckServer(ProductServer):
    def __init__(
        self,
        env: sp.Environment,
        params: pr.ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, product: Product):
        # print(
        #     f"At time t = {self.env.now}, QACheckServer RECEIVE product = {product.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time,
        ))
        # print(
        #     f"At time t = {self.env.now}, QACheckServer START product = {product.name}, duration = {service_time}")
        yield self.env.timeout(service_time)

    def stop(self):
        return 

class DispatcherServer(ProductServer):
    def __init__(self, env: sp.Environment, params: pr.ServerParams) -> None:
        self.env = env
        self.params = params
        super().__init__()

    
    def process(self, product: Product):
        # print(
        #     f"At time t = {self.env.now}, DispatcherServer RECEIVE product = {product.name}")

        service_time = max(1, np.random.exponential(self.params.mean_service_time))
        
        # print(
        #     f"At time t = {self.env.now}, DispatcherServer START product = {product.name}, duration = {service_time}")
        
        yield self.env.timeout(service_time)
        
        # print(
        #     f"At time t = {self.env.now}, DispatcherServer FINISH product = {product.name}")

    def stop(self):
        return

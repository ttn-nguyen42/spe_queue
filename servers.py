from visitor import Visitor
from functools import wraps
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
    
    def patch_resource(resource, pre=None, post=None):
        """Patch *resource* so that it calls the callable *pre* before each
        put/get/request/release operation and the callable *post* after each
        operation.  The only argument to these functions is the resource
        instance.
        
        """
        def get_wrapper(func):
            # Generate a wrapper for put/get/request/release
            @wraps(func)
            def wrapper(*args, **kwargs):
                # This is the actual wrapper
                # Call "pre" callback
                if pre:
                    pre(resource)

                # Perform actual operation
                ret = func(*args, **kwargs)

                # Call "post" callback
                if post:
                    post(resource)

                return ret
            return wrapper

        # Replace the original operations with our wrapper
        for name in ['put', 'get', 'request', 'release']:
            if hasattr(resource, name):
                setattr(resource, name, get_wrapper(getattr(resource, name)))

    def monitor(data, resource):
        """This is our monitoring callback."""
        item = (
            resource._env.now,  # The current simulation time
            resource.count,  # The number of users
            len(resource.queue),  # The number of queued processes
        )
        data.append(item)

class ReceptionServer(VisitorServer):
    def __init__(self, env: sp.Environment, params: pr.ServerParams) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, ReceptionServer RECEIVE visitor = {visitor.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time))
        print(
            f"At time t = {self.env.now}, ReceptionServer START visitor = {visitor.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(
            f"At time t = {self.env.now}, ReceptionServer FINISH visitor = {visitor.name}")

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
        print(
            f"At time t = {self.env.now}, RoomServer RECEIVE visitor = {visitor.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time,
        ))
        print(
            f"At time t = {self.env.now}, RoomServer START visitor = {visitor.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(
            f"At time t = {self.env.now}, RoomServer FINISH visitor = {visitor.name}")

    def stop(self):
        return


class HallwayServer(VisitorServer):
    def __init__(
        self,
        env: sp.Environment,
        params: pr.ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        super().__init__()

    def process(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, HallwayServer RECEIVE visitor = {visitor.name}")
        service_time = max(1, np.random.exponential(
            self.params.mean_service_time,
        ))
        print(
            f"At time t = {self.env.now}, HallwayServer START visitor = {visitor.name}, duration = {service_time}")
        yield self.env.timeout(service_time)
        print(
            f"At time t = {self.env.now}, HallwayServer FINISH visitor = {visitor.name}")

    def stop(self):
        return

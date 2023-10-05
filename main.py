import simpy as sp
import numpy as np
import params as pr
from visitor import Visitor
from systems import System, Reception


class Generator:
    def __init__(
        self,
        env: sp.Environment,
        params: pr.GeneratorParams,
        reception: System,
    ) -> None:
        self.env = env
        self.params = params
        self.reception = reception

    def generate(self):
        while True:
            interarrival = np.random.exponential(
                self.params.mean_interarrival_time)
            yield self.env.timeout(interarrival)
            print(f"Message sent at {self.env.now}")
            self.reception.add_visitor(visitor=Visitor(name="ABC"))

    def run(self):
        self.env.process(self.generate())


if __name__ == "__main__":
    env = sp.Environment()

    reception = Reception(
        env=env,
        params=pr.SystemParams(name="Reception", max_servers=3),
        queue_params=pr.QueueParams(max_queue_size=2000),
        server_params=pr.ServerParams(mean_service_time=3)
    )

    gen = Generator(
        env=env,
        params=pr.GeneratorParams(
            num_rooms=1,
            mean_interarrival_time=1
        ),
        reception=reception,
    )

    reception.run()
    gen.run()
    env.run(until=pr.SIM_DURATION)

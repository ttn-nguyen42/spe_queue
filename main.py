import simpy as sp
import numpy as np
import params as pr
from product import Product
from systems import ProductionLine, QACheck, Dispatcher
from base_systems import System, SystemScheduleResult
from typing import List
import uuid
from prettytable import PrettyTable
import json

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
            print(f"At time t = {self.env.now}, Generate NEW_VISITOR")
            self.reception.add_product(
                product=Product(name=self._random_name()))

    def _random_name(self) -> str:
        return uuid.uuid4()

    def run(self):
        self.env.process(self.generate())

class Factory(System):
    def __init__(
            self,
            env: sp.Environment,
            params: pr.SystemParams,
            queue_params: pr.QueueParams,
            server_params: pr.ServerParams,
            production_lines: list[ProductionLine],
            qa_checks: list[QACheck]
    ) -> None:
        self.production_lines = production_lines
        self.qa_checks = qa_checks
        super().__init__(env, params, queue_params, server_params)

    def run(self):
        super().run()
        
class Factory:
    def __init__(self, config_path: str) -> None:
        self.env = sp.Environment()
        self.dat = None
        self.configure(config_path=config_path)

        self.products = self._generate_rooms(
        )

        self.hallway.set_rooms(self.rooms)

        reception_cfg = self.dat["reception"]
        self.reception = Reception(
            env=self.env,
            params=pr.SystemParams(
                name=reception_cfg["name"],
                max_servers=reception_cfg["max_servers"],
            ),
            queue_params=pr.QueueParams(
                max_queue_size=reception_cfg["max_queue_size"],
            ),
            server_params=pr.ServerParams(
                mean_service_time=reception_cfg["mean_service_time"],
            ),
            rooms=self.rooms,
            hallway=self.hallway,
        )

        generator_cfg = self.dat["generator"]
        self.generator = Generator(
            env=self.env,
            params=pr.GeneratorParams(
                mean_interarrival_time=generator_cfg["mean_interarrival_time"]
            ),
            reception=self.reception,
        )

        sim_time = self.dat["simulation_time"]
        pr.SIM_DURATION = sim_time

    # MMN0208: Add close function
    def close(self):
        yield self.env.timeout(pr.SIM_DURATION)
        print(
            f"------------------------\nAt time t =  {self.env.now}, Museum CLOSES\n------------------------")
        self.hallway.stop_idle()
        self.hallway.stop_active()
        self.reception.stop_idle()
        self.reception.stop_active()
        for r in self.rooms:
            r.stop_idle()
            r.stop_active()
        return

    def configure(self, config_path: str):
        f = open(config_path)
        self.dat = json.load(f)
        f.close()
        return

    def open(self):
        print(
            f"------------------------\nAt time t =  {self.env.now}, Museum OPENS\n------------------------")
        self._start_rooms()
        # self.hallway.run()
        self.dispatcher.run()
        self.generator.run()
        proc = self.env.process(self.close())
        self.env.run(until=proc)
        self.stats()

    def _generate_rooms(self) -> List[Product]:
        products: List[Product] = []
        cfgs = self.dat["products"]
        for product_cfg in cfgs:
            products.append(Product(
                env=self.env,
                server_params=pr.ServerParams(
                    mean_service_time=product_cfg["mean_service_time"],
                ),
                queue_params=pr.QueueParams(
                    max_queue_size=product_cfg["max_queue_size"],
                ),
                params=pr.SystemParams(
                    name=room_cfg["name"], max_servers=room_cfg["max_servers"],
                ),
            ))
        return products

    def _start_rooms(self):
        i = 0
        for r in self.products:
            r.run()

    def stats(self):
        print(
            f"------------------------\nSimulation time = {pr.SIM_DURATION}\n------------------------")
        tb = PrettyTable(["system_name", "total_idle_time",
                         "avg_service_time", "avg_wait_time", "visitors"])
        tb.add_row(self.dispatcher.get_stats().list_stats())
        for r in self.rooms:
            tb.add_row(r.get_stats().list_stats())
        tb.align["system_name"] = "l"
        print(tb)


if __name__ == "__main__":
    ms = Factory(config_path="./config.json")
    ms.open()

import simpy as sp
import numpy as np
import params as pr
from product import Product
from systems import ProductionLine, QACheck, Dispatcher, Destination
from base_systems import System, SystemScheduleResult
from typing import List
import uuid
from prettytable import PrettyTable
import json


class GeneratorStatistics:
    def __init__(self, env: sp.Environment) -> None:
        self.env = env

        self.reception_overflow_count: int = 0
        self.total_generated: int = 0
        self.total_interarrival_time: float = 0.0

    def add_overflow_count(self):
        self.reception_overflow_count += 1

    def add_total_generated(self):
        self.total_generated += 1

    def avg_interarrival_time(self) -> float:
        if self.total_generated == 0:
            return 0.0
        return self.total_interarrival_time / self.total_generated

    def update_interarrival_time(self, last_time: float):
        self.total_interarrival_time += last_time

    def list_stats(self) -> List:
        return [self.reception_overflow_count, self.total_generated]

    def __str__(self) -> str:
        return f"""
total_generated: {self.total_generated}
reception_overflow_count: {self.reception_overflow_count}
avg_interarrival_time: {round(self.avg_interarrival_time(), 5)}
"""


class Generator:
    def __init__(
        self,
        env: sp.Environment,
        params: pr.GeneratorParams,
        dispatcher: Dispatcher,
    ) -> None:
        self.env = env
        self.params = params
        self.dispatcher = dispatcher
        self.current_id = 0
        self.stats = GeneratorStatistics(env=self.env)

    def generate(self):
        while True:
            interarrival = np.random.exponential(
                self.params.mean_interarrival_time)
            yield self.env.timeout(interarrival)
            print(f"At time t = {self.env.now}, Generate NEW_PRODUCT")
            self.stats.update_interarrival_time(last_time=interarrival)
            self.stats.add_total_generated()
            if self.dispatcher.is_full():
                self.stats.add_overflow_count()
                print(f"Generator DISPATCHER_FULL")
                continue

            self.dispatcher.add_product(
                product=Product(name=self._random_name()))

    def _random_name(self) -> str:
        curr_id = self.current_id
        self.current_id += 1
        return curr_id

    def get_stats(self) -> GeneratorStatistics:
        return self.stats

    def run(self):
        self.env.process(self.generate())


class Factory:
    def __init__(self, config_path: str) -> None:
        self.env = sp.Environment()
        self.dat = None
        self.configure(config_path=config_path)

        self.products = self._generate_systems()

        # self.products += self._generate_systems_check()
        dispatcher_cfg = self.dat["dispatcher"]

        # Initialize dispatcher
        dispatcher_go_to = dispatcher_cfg["go_to"]
        product_lines: list[Destination] = []
        for place in dispatcher_go_to:
            name = place["name"]
            probability = place["probability"]
            system = self.products[name]
            product_lines.append(Destination(
                name=name,
                probability=probability,
                system=system
            ))

        self.dispatcher = Dispatcher(
            env=self.env,
            params=pr.SystemParams(
                name=dispatcher_cfg["name"],
                max_servers=dispatcher_cfg["max_servers"],
            ),
            queue_params=pr.QueueParams(
                max_queue_size=dispatcher_cfg["max_queue_size"],
            ),
            server_params=pr.ServerParams(
                mean_service_time=dispatcher_cfg["mean_service_time"],
            ),
            production_lines=product_lines
        )

        generator_cfg = self.dat["generator"]
        self.generator = Generator(
            env=self.env,
            params=pr.GeneratorParams(
                mean_interarrival_time=generator_cfg["mean_interarrival_time"]
            ),
            dispatcher=self.dispatcher,
        )

        sim_time = self.dat["simulation_time"]
        pr.SIM_DURATION = sim_time

    # MMN0208: Add close function
    def close(self):
        yield self.env.timeout(pr.SIM_DURATION)
        print(
            f"------------------------\nAt time t =  {self.env.now}, Factory CLOSES\n------------------------")
        self.dispatcher.stop()
        for line in self.products:
            self.products[line].stop()

        for qa in self.qa_check:
            self.qa_check[qa].stop()
        return

    def configure(self, config_path: str):
        f = open(config_path)
        self.dat = json.load(f)
        f.close()
        return

    def open(self):
        print(
            f"------------------------\nAt time t =  {self.env.now}, Factory OPENS\n------------------------")
        self._start_products()
        self.dispatcher.run()
        self.generator.run()
        proc = self.env.process(self.close())
        self.env.run(until=proc)
        self.stats()

    def _generate_systems(self) -> dict[str, ProductionLine]:
        productionline: dict[str, ProductionLine] = {}
        qa_check: dict[str, QACheck] = {}

        qa_cfgs = self.dat["qa_check"]

        # Initialize all QA check lines
        for cfg in qa_cfgs:
            name = cfg["name"]

            qa_check[name] = QACheck(
                env=self.env,
                params=pr.SystemParams(
                    name=name,
                    max_servers=cfg["max_servers"]
                ),
                queue_params=pr.QueueParams(
                    max_queue_size=cfg["max_queue_size"]
                ),
                server_params=pr.ServerParams(
                    mean_service_time=cfg["mean_service_time"]
                ),
                go_to=[]
            )

        self.qa_check = qa_check

        print(f"QA checks {qa_check}")

        cfgs = self.dat["productionlines"]

        # Initialize all production lines
        for productionline_cfg in cfgs:
            name = productionline_cfg["name"]
            go_to = productionline_cfg["go_to"]

            # collect all destination QA check lines for a production line
            destination_qa_check = []
            if len(go_to) > 0:
                for where in go_to:
                    dest_name = where["name"]

                    if dest_name == "exit":
                        destination = Destination(
                            name=dest_name,
                            probability=where["probability"],
                            system=None
                        )
                        destination_qa_check.append(destination)
                        continue

                    destination = Destination(
                        name=dest_name,
                        probability=where["probability"],
                        system=qa_check[dest_name]
                    )
                    destination_qa_check.append(destination)

            productionline[name] = ProductionLine(
                env=self.env,
                params=pr.SystemParams(
                    name=productionline_cfg["name"],
                    max_servers=productionline_cfg["max_servers"],
                ),
                queue_params=pr.QueueParams(
                    max_queue_size=productionline_cfg["max_queue_size"],
                ),
                server_params=pr.ServerParams(
                    mean_service_time=productionline_cfg["mean_service_time"],
                ),
                qa_check=destination_qa_check,
            )

        print(f"Production lines: {productionline}")

        for cfg in qa_cfgs:
            name = cfg["name"]

            qa_check_line = qa_check[name]
            destinations: list[ProductionLine] = []

            go_to_list = cfg["go_to"]

            for dest in go_to_list:
                name = dest["name"]
                probability = dest["probability"]

                if name == "exit":
                    destinations.append(Destination(
                        name=name,
                        probability=probability,
                        system=None,
                    ))
                    continue

                system = productionline[name]

                destinations.append(Destination(
                    name=name,
                    probability=probability,
                    system=system
                ))

            # set product line destinations for QA check lines
            qa_check_line.set_product_lines_destinations(
                destinations=destinations)

        return productionline

    def _start_products(self):
        for line in self.products:
            self.products[line].run()

        for qa in self.qa_check:
            self.qa_check[qa].run()

    def stats(self):
        print(
            f"------------------------\nSimulation time = {pr.SIM_DURATION}\n------------------------")
        tb = PrettyTable(["system_name", "total_idle_time",
                         "avg_service_time", "avg_wait_time", "processed_products", "remaining_products", "utilization"])
        tb.add_row(self.dispatcher.get_stats().list_stats())
        for line in self.products:
            r = self.products[line]
            tb.add_row(r.get_stats().list_stats())

        for qa in self.qa_check:
            r = self.qa_check[qa]
            tb.add_row(r.get_stats().list_stats())
        tb.align["system_name"] = "l"

        print(tb)

        print(
            f"------------------------\nGenerator statistics\n------------------------")
        print(self.generator.get_stats())


if __name__ == "__main__":
    ms = Factory(config_path="./config.json")
    ms.open()

import simpy as sp
import numpy as np
import params as pr
from visitor import Visitor
from systems import System, Reception, Room, Hallway
from typing import List
import uuid
from prettytable import PrettyTable
import json
import random
import time

random.seed(time.time())


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
        reception: Reception,
    ) -> None:
        self.env = env
        self.params = params
        self.reception = reception
        self.stats = GeneratorStatistics(env=self.env)

    def generate(self):
        while True:
            interarrival = np.random.exponential(
                self.params.mean_interarrival_time)
            yield self.env.timeout(interarrival)
            print(f"At time t = {self.env.now}, Generator NEW_VISITOR")
            self.stats.update_interarrival_time(last_time=interarrival)
            self.stats.add_total_generated()
            if self.reception.is_full():
                self.stats.add_overflow_count()
                print(f"Generator RECEPTION_FULL")
                continue
            
            self.reception.add_visitor(
                visitor=Visitor(name=self._random_name()))

    def _random_name(self) -> str:
        return uuid.uuid4()

    def get_stats(self) -> GeneratorStatistics:
        return self.stats

    def run(self):
        self.env.process(self.generate())


class Museum:
    def __init__(self, config_path: str) -> None:
        self.env = sp.Environment()
        self.dat = None
        self.configure(config_path=config_path)

        hallway_cfg = self.dat["hallway"]
        self.hallway = Hallway(
            env=self.env,
            params=pr.SystemParams(
                name=hallway_cfg["name"],
                max_servers=hallway_cfg["max_servers"],
            ),
            queue_params=pr.QueueParams(
                max_queue_size=hallway_cfg["max_queue_size"]),
            server_params=pr.ServerParams(
                mean_service_time=hallway_cfg["mean_service_time"]),
            rooms=[]
        )

        self.rooms = self._generate_rooms(
            hallway=self.hallway,
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
        self.hallway.stop()
        self.reception.stop()
        for r in self.rooms:
            r.stop()
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
        self.hallway.run()
        self.reception.run()
        self.generator.run()
        proc = self.env.process(self.close())
        self.env.run(until=proc)
        self.stats()

    def _generate_rooms(self, hallway: Hallway) -> List[Room]:
        rooms: List[Room] = []
        cfgs = self.dat["rooms"]
        for room_cfg in cfgs:
            rooms.append(Room(
                env=self.env,
                server_params=pr.ServerParams(
                    mean_service_time=room_cfg["mean_service_time"],
                ),
                queue_params=pr.QueueParams(
                    max_queue_size=room_cfg["max_queue_size"],
                ),
                params=pr.SystemParams(
                    name=room_cfg["name"], max_servers=room_cfg["max_servers"],
                ),
                hallway=hallway,
            ))
        return rooms

    def _start_rooms(self):
        i = 0
        for r in self.rooms:
            r.run()

    def stats(self):
        print(
            f"------------------------\nSimulation time = {pr.SIM_DURATION}\n------------------------")
        tb = PrettyTable(["system_name", "total_idle_time",
                         "avg_service_time", "avg_wait_time", "processed_visitors", "remaining_visitors", "utilization"])
        tb.add_row(self.reception.get_stats().list_stats())
        tb.add_row(self.hallway.get_stats().list_stats(), divider=True)
        for r in self.rooms:
            tb.add_row(r.get_stats().list_stats())
        tb.align["system_name"] = "l"

        print(tb)

        print(
            f"------------------------\nGenerator statistics\n------------------------")
        print(self.generator.get_stats())


if __name__ == "__main__":
    ms = Museum(config_path="./config.json")
    ms.open()

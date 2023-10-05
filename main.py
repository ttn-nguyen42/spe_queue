import simpy as sp
import numpy as np
import params as pr
from visitor import Visitor
from systems import System, Reception, Room, Hallway
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
            print(f"Genrator NEW_VISITOR {self.env.now}")
            self.reception.add_visitor(
                visitor=Visitor(name=self._random_name()))

    def _random_name(self) -> str:
        return uuid.uuid4()

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
                max_servers=1,
            ),
            queue_params=pr.QueueParams(
                max_queue_size=hallway_cfg["max_queue_size"]),
            server_params=None,
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
            f"------------------------\nSimulation end at {self.env.now}\n------------------------")
        self.hallway.idle_proc.interrupt()
        self.reception.idle_proc.interrupt()
        for r in self.rooms:
            r.idle_proc.interrupt()
        return

    def configure(self, config_path: str):
        f = open(config_path)
        self.dat = json.load(f)
        f.close()
        return

    def open(self):
        self._start_rooms()
        self.hallway.run()
        self.reception.run()
        self.generator.run()
        proc = self.env.process(self.close())
        self.env.run(until=proc)
        self.stats()

    def _generate_rooms(self, hallway: Hallway) -> List[Room]:
        i = 0
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
            i += 1
        return rooms

    def _start_rooms(self):
        i = 0
        for r in self.rooms:
            r.run()

    def stats(self):
        tb = PrettyTable(["system_name", "avg_idle_time",
                         "avg_service_time", "avg_wait_time"])
        tb.add_row(self.reception.get_stats().list_stats())
        tb.add_row(self.hallway.get_stats().list_stats(), divider=True)
        for r in self.rooms:
            tb.add_row(r.get_stats().list_stats())
        tb.align["system_name"] = "l"
        print(tb)


if __name__ == "__main__":
    ms = Museum(config_path="./config.json")
    ms.open()

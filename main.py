import simpy as sp
import numpy as np
import params as pr
from visitor import Visitor
from systems import System, Reception, Room, Hallway
from typing import List
import uuid


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
    def __init__(self) -> None:
        self.env = sp.Environment()

        self.hallway = Hallway(
            env=self.env,
            params=pr.SystemParams(name="hallway-0", max_servers=1),
            queue_params=pr.QueueParams(max_queue_size=1000),
            server_params=None,
            rooms=[]
        )

        self.rooms = self._generate_rooms(
            amount=20,
            hallway=self.hallway,
        )

        self.hallway.set_rooms(self.rooms)

        self.reception = Reception(
            env=self.env,
            params=pr.SystemParams(name="reception", max_servers=3),
            queue_params=pr.QueueParams(max_queue_size=2000),
            server_params=pr.ServerParams(mean_service_time=3),
            rooms=self.rooms,
        )

        self.generator = Generator(
            env=self.env,
            params=pr.GeneratorParams(
                num_rooms=1,
                mean_interarrival_time=1
            ),
            reception=self.reception,
        )

    def open(self):
        self._start_rooms()
        self.hallway.run()
        self.reception.run()
        self.generator.run()
        self.env.run(until=pr.SIM_DURATION)
        self.stats()

    def _generate_rooms(self, hallway: Hallway, amount: int = 1) -> List[Room]:
        i = 0
        rooms: List[Room] = []
        while i < amount:
            rooms.append(Room(
                env=self.env,
                server_params=pr.ServerParams(mean_service_time=5),
                queue_params=pr.QueueParams(max_queue_size=2000),
                params=pr.SystemParams(name=f"room-{i}", max_servers=20),
                hallway=hallway,
            ))
            i += 1
        return rooms

    def _start_rooms(self):
        i = 0
        for r in self.rooms:
            r.run()

    def stats(self):
        # Should be able to save these to a file
        print("#############")
        print("Statistics:")
        print(self.reception.get_stats())
        print(self.hallway.get_stats())
        for r in self.rooms:
            print(r.get_stats())


if __name__ == "__main__":
    ms = Museum()
    ms.open()

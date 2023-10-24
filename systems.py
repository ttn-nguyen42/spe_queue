import simpy as sp
from params import ServerParams, QueueParams, SystemParams
from visitor import Visitor
from servers import ReceptionServer, RoomServer, HallwayServer
import random
from base_systems import System, SystemScheduleResult


class Room(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            hallway: System = None) -> None:
        self.hallway = hallway
        super().__init__(env, params, queue_params, server_params)

    def set_hallway(self, hallway: System):
        self.hallway = hallway
        return self

    # Moves visitor to hallway

    def schedule(self):
        while True:
            res, visitor, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_VISITOR:
                    server = RoomServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        visitor=visitor, req=req, server=server))
                    self._move_to_hallway(visitor=visitor)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    def _move_to_hallway(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, Room TO_HALLWAY visitor = {visitor.get_name()}")
        self.hallway.add_visitor(visitor=visitor)
        visitor.visited(self.get_name())

    def run(self):
        super().run()
        self.env.process(self.schedule())


class Hallway(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            rooms: list[Room] = None) -> None:
        self.rooms = rooms
        super().__init__(env, params, queue_params, server_params)

    def set_rooms(self, rooms: list[System]):
        self.rooms = rooms
        return self

    # Moves its visitor to rooms
    def schedule(self):
        while True:
            res, visitor, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_VISITOR:
                    server = HallwayServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        visitor=visitor, req=req, server=server))
                    self._send_to_unvisited_room(visitor=visitor)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    def _send_to_unvisited_room(self, visitor: Visitor):
        # Find unvisited room and returns an index
        # self.rooms
        all_rooms = self.rooms
        available_rooms = []
        for i, r in enumerate(all_rooms):
            if visitor.has_visited(r.get_name()):
                available_rooms.append(r)
        if len(available_rooms) == 0:
            print("Hallway VISITOR_DONE")
            return
        available_rooms.sort(key=self.availability)
        available_rooms[0].add_visitor(visitor=visitor)
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())


class Reception(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            rooms: list[Room] = None,
            hallway: Hallway = None
    ) -> None:
        self.rooms = rooms
        self.hallway = hallway
        super().__init__(env, params, queue_params, server_params)

    def set_rooms(self, rooms: list[Room]):
        self.rooms = rooms
        return self

    def set_hallway(self, hallway: Hallway):
        self.hallway = hallway
        return self

    def schedule(self):
        while True:
            res, visitor, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_VISITOR:
                    server = ReceptionServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        visitor=visitor, req=req, server=server))
                    self._move_to_room(visitor=visitor)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    # Move visitor to room
    def _move_to_room(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, Reception MOVE_TO_ROOM visitor = {visitor.get_name()}")

        # Check which room available
        avail_room: list[System] = []

        for room in self.rooms:
            if room.is_available() and not room.is_full():
                avail_room.append(room)

        if len(avail_room) > 0:
            avail_room.sort(key=self.availability)
            avail_room[0].add_visitor(visitor=visitor)
            return

        self.hallway.add_visitor(visitor=visitor)
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

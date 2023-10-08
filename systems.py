import simpy as sp
import params as pr
from visitor import Visitor, Entry, VisitorStatistics
from servers import ReceptionServer, RoomServer, HallwayServer
import random
from base_systems import System


class Room(System):
    def __init__(
            self,
            env: sp.Environment,
            params: pr.SystemParams,
            queue_params: pr.QueueParams,
            server_params: pr.ServerParams,
            hallway: System = None) -> None:
        self.hallway = hallway
        self.active_proc = None
        self.idle_proc = None
        self.is_idle = True
        super().__init__(env, params, queue_params, server_params)

    def set_hallway(self, hallway: System):
        self.hallway = hallway
        return self

    def add_visitor(self, visitor: Visitor):
        stats = VisitorStatistics()
        ent = Entry(
            id=self.get_name(),
            stats=stats,
        )
        visitor.queues_visited.append(ent)
        stats.start_wait_time = self.env.now

        super().add_visitor(visitor=visitor)

        if self.is_idle:
            self.stop_idle()

        if self.is_available():
            self.stop_active()

    def get_name(self) -> str:
        return self.params.name

    def stop_idle(self):
        self.is_idle = False
        if self.idle_proc is not None and not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    def stop_active(self):
        if self.active_proc is not None and not self.active_proc.triggered:
            self.active_proc.interrupt()

    def _active(self):
        try:
            active_start = self.env.now
            print(
                f"At time t = {active_start}, Room {self.get_name()} ACTIVE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            active_end = self.env.now
            print(
                f"At time t = {active_end}, Room {self.get_name()} ACTIVE ends")

    # Serve visitor for visting the room
    def serve(self, visitor: Visitor, req: sp.Resource):
        service_start = self.env.now
        server = RoomServer(
            env=self.env,
            params=self.server_params,
        )
        yield from server.process(visitor=visitor)
        service_end = self.env.now
        self.stats.update_service_time(service_end - service_start)
        # Move to a hallway
        self._move_to_hallway(visitor=visitor)
        self.available_servers.release(request=req)

        self.stats.update_visitor_count()

        if self.is_available():
            self.stop_active()

    # Moves visitor to hallway
    def schedule(self):
        while True:
            if not self.is_empty():
                if self.is_available():
                    req = self.available_servers.request()
                    print(
                        f"Room {self.get_name()} servers count = {self.available_servers.count}/{self.available_servers.capacity}")
                    self.stats.update_service_requests()
                    visitor = self.find_visitor()
                    visitor.update_wait_time(
                        id=self.get_name(),
                        end=self.env.now)

                    self.stats.update_wait_time(
                        wait_time=visitor.get_wait_time(id=self.get_name()))
                    yield req
                    self.env.process(self.serve(visitor=visitor, req=req))
                    continue
            else:
                print(
                    f"At time t = {self.env.now}, Room {self.get_name()} NO_VISITOR idle start")
            if self.is_active():
                active_state = self._active()
                self.active_proc = self.env.process(active_state)
                yield self.active_proc
            else:
                self.is_idle = True
                idle_timeout = self._idle()
                self.idle_proc = self.env.process(idle_timeout)
                yield self.idle_proc

    def _idle(self):
        try:
            idle_start = self.env.now
            print(f"At time t = {idle_start}, Room IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            idle_end = self.env.now
            print(f"At time t = {idle_end}, Room IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _move_to_hallway(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, Room TO_HALLWAY visitor = {visitor.get_name()}")
        self.hallway.add_visitor(visitor=visitor)

        visitor.visited(self)

        self.hallway.add_visitor(visitor=visitor)

    def run(self):
        self.env.process(self.schedule())

    def calculate_in_queue_wait_time(self):
        remaining_visitors = self.queue.visitors
        self.stats.in_queue_at_end = len(remaining_visitors)
        for v in remaining_visitors:
            self.stats.update_wait_time(
                wait_time=v.get_wait_time(id=self.get_name()))

    def stop(self):
        self.stop_idle()
        self.stop_active()
        self.calculate_in_queue_wait_time()


class Hallway(System):
    def __init__(
            self,
            env: sp.Environment,
            params: pr.SystemParams,
            queue_params: pr.QueueParams,
            server_params: pr.ServerParams,
            rooms: list[Room] = None) -> None:
        self.rooms = rooms
        self.active_proc = None
        self.idle_proc = None
        self.is_idle = True
        super().__init__(env, params, queue_params, server_params)

    def set_rooms(self, rooms: list[Room]):
        self.rooms = rooms
        return self

    def get_name(self) -> str:
        return self.params.name

    def add_visitor(self, visitor: Visitor):
        stats = VisitorStatistics()
        ent = Entry(
            id=self.get_name(),
            stats=stats,
        )
        visitor.queues_visited.append(ent)
        stats.start_wait_time = self.env.now

        super().add_visitor(visitor=visitor)

        if self.is_idle:
            self.stop_idle()

        if self.is_available():
            self.stop_active()

    def stop_idle(self):
        self.is_idle = False
        if self.idle_proc is not None and not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    # Should be doing nothing
    def serve(self, visitor: Visitor, req: sp.Resource):
        service_start = self.env.now
        server = HallwayServer(
            env=self.env,
            params=self.server_params,
        )
        yield from server.process(visitor=visitor)
        service_end = self.env.now
        self.stats.update_service_time(service_end - service_start)
        self.available_servers.release(request=req)
        self.stats.update_visitor_count()

        if self.is_available():
            self.stop_active()

    # Moves its visitor to rooms
    def schedule(self):
        while True:
            if not self.is_empty():
                if self.is_available():
                    print(
                        f"Hallway servers count = {self.available_servers.count}/{self.available_servers.capacity}")
                    req = self.available_servers.request()
                    self.stats.update_service_requests()
                    visitor = self.find_visitor()
                    visitor.update_wait_time(
                        id=self.get_name(),
                        end=self.env.now)
                    self.stats.update_wait_time(
                        wait_time=visitor.get_wait_time(id=self.get_name()))
                    self._send_to_unvisited_room(visitor=visitor)
                    yield req
                    self.env.process(self.serve(visitor=visitor, req=req))
                    continue
            else:
                print(
                    f"At time t = {self.env.now}, Hallway {self.get_name()} NO_VISITOR idle start")
            if self.is_active():
                active_state = self._active()
                self.active_proc = self.env.process(active_state)
                yield self.active_proc
            else:
                self.is_idle = True
                idle_timeout = self._idle()
                self.idle_proc = self.env.process(idle_timeout)
                yield self.idle_proc

    def _idle(self):
        try:
            idle_start = self.env.now
            print(f"At time t = {idle_start}, Hallway IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            idle_end = self.env.now
            print(f"At time t = {idle_end}, Hallway IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _send_to_unvisited_room(self, visitor: Visitor) -> int:
        # Find unvisited room and returns an index
        # self.rooms
        all_rooms = self.rooms
        available_rooms = []
        for i, r in enumerate(all_rooms):
            if visitor.has_visited(r.get_name()):
                available_rooms.append(i)
        if len(available_rooms) == 0:
            print("Hallway VISITOR_DONE")
            return
        chosen = random.choice(available_rooms)
        all_rooms[chosen].add_visitor(visitor=visitor)
        return

        for index, room in enumerate(self.rooms):
            if not visitor.has_visited(room):
                return index

        return -1

    def run(self):
        self.env.process(self.schedule())

    def calculate_in_queue_wait_time(self):
        remaining_visitors = self.queue.visitors
        self.stats.in_queue_at_end = len(remaining_visitors)
        for v in remaining_visitors:
            self.stats.update_wait_time(
                wait_time=v.get_wait_time(id=self.get_name()))

    def stop_active(self):
        if self.active_proc is not None and not self.active_proc.triggered:
            self.active_proc.interrupt()

    def _active(self):
        try:
            active_start = self.env.now
            print(
                f"At time t = {active_start}, Room {self.get_name()} ACTIVE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            active_end = self.env.now
            print(
                f"At time t = {active_end}, Room {self.get_name()} ACTIVE ends")

    def stop(self):
        self.stop_idle()
        self.stop_active()
        self.calculate_in_queue_wait_time()


class Reception(System):
    def __init__(
            self,
            env: sp.Environment,
            params: pr.SystemParams,
            queue_params: pr.QueueParams,
            server_params: pr.ServerParams,
            rooms: list[Room] = None,
            hallway: Hallway = None
    ) -> None:
        self.rooms = rooms
        self.hallway = hallway
        self.idle_proc = None
        self.active_proc = None
        self.is_idle = True
        super().__init__(env, params, queue_params, server_params)

    def set_rooms(self, rooms: list[Room]):
        self.rooms = rooms
        return self

    def set_hallway(self, hallway: Hallway):
        self.hallway = hallway
        return self

    def get_name(self) -> str:
        return self.params.name

    def serve(self, visitor: Visitor, req: sp.Resource):
        service_start = self.env.now
        server = ReceptionServer(
            env=self.env,
            params=self.server_params,
        )
        yield from server.process(visitor=visitor)
        service_end = self.env.now
        self.stats.update_service_time(service_end - service_start)
        # Move from reception to a random room
        self._move_to_room(visitor=visitor)
        self.available_servers.release(request=req)
        self.stats.update_visitor_count()

        if self.is_available():
            self.stop_active()

    def add_visitor(self, visitor: Visitor):
        stats = VisitorStatistics()
        ent = Entry(
            id=self.get_name(),
            stats=stats,
        )
        visitor.queues_visited.append(ent)
        stats.start_wait_time = self.env.now

        super().add_visitor(visitor=visitor)

        if self.is_idle:
            self.stop_idle()

        if self.is_available():
            self.stop_active()

    def stop_idle(self):
        self.is_idle = False
        if self.idle_proc is not None and not self.idle_proc.triggered:
            self.idle_proc.interrupt()

    def stop_active(self):
        if self.active_proc is not None and not self.active_proc.triggered:
            self.active_proc.interrupt()

    def schedule(self):
        while True:
            # There's a message
            if not self.is_empty():
                if self.is_available():
                    # There's a server
                    req = self.available_servers.request()
                    print(
                        f"Reception servers count = {self.available_servers.count}/{self.available_servers.capacity}")
                    self.stats.update_service_requests()
                    visitor = self.find_visitor()

                    visitor.update_wait_time(
                        id=self.get_name(),
                        end=self.env.now)

                    self.stats.update_wait_time(
                        wait_time=visitor.get_wait_time(id=self.get_name()))

                    yield req
                    self.env.process(self.serve(visitor=visitor, req=req))
                    continue
            else:
                print(
                    f"At time t = {self.env.now}, Reception NO_VISITOR idle start")
            if self.is_active():
                active_state = self._active()
                self.active_proc = self.env.process(active_state)
                yield self.active_proc
            else:
                self.is_idle = True
                idle_timeout = self._idle()
                self.idle_proc = self.env.process(idle_timeout)
                yield self.idle_proc

    def _idle(self):
        try:
            idle_start = self.env.now
            print(f"At time t = {idle_start}, Reception IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            idle_end = self.env.now
            print(f"At time t = {idle_end}, Reception IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _active(self):
        try:
            active_start = self.env.now
            print(f"At time t = {active_start}, Reception ACTIVE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            active_end = self.env.now
            print(f"At time t = {active_end}, Reception ACTIVE ends")

    # Move visitor to room
    def _move_to_room(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, Reception MOVE_TO_ROOM visitor = {visitor.get_name()}")

        # Choose a random room to move visitor to
        # self.rooms
        # Room name: self.rooms[i].get_name()

        # Check which room available
        avail_room: list[System] = []

        for room in self.rooms:
            if room.is_available() and not room.is_full():
                avail_room.append(room)

        if len(avail_room) > 0:
            room_select = random.choice(avail_room)
            room_select.add_visitor(visitor=visitor)
            return

        self.hallway.add_visitor(visitor=visitor)
        return

    def run(self):
        self.env.process(self.schedule())

    def calculate_in_queue_wait_time(self):
        remaining_visitors = self.queue.visitors
        self.stats.in_queue_at_end = len(remaining_visitors)
        for v in remaining_visitors:
            self.stats.update_wait_time(
                wait_time=v.get_wait_time(id=self.get_name()))

    def stop(self):
        self.stop_idle()
        self.stop_active()
        self.calculate_in_queue_wait_time()

import simpy as sp
import params as pr
from visitor import Visitor
from qs import Queue
from servers import ReceptionServer, RoomServer
from system_stats import SystemStatistics
import random

class System:
    """
    Manages a queue and its servers
    """

    def __init__(
        self,
        env: sp.Environment,
        params: pr.SystemParams,
        queue_params: pr.QueueParams,
        server_params: pr.ServerParams,
    ) -> None:
        self.env = env
        self.params = params
        self.server_params = server_params
        self.queue = Queue(params=queue_params)
        self.available_servers = sp.Resource(
            self.env, capacity=params.max_servers)
        self.stats = SystemStatistics(system_name=self.params.name)
        pass

    def get_stats(self) -> SystemStatistics:
        return self.stats

    def add_visitor(self, visitor: Visitor):
        self.queue.enqueue(visitor=visitor)

    def find_visitor(self) -> Visitor:
        try:
            return self.queue.dequeue()
        except Exception:
            return None

    def is_empty(self) -> bool:
        return self.queue.is_empty()

    def is_full(self) -> bool:
        return self.queue.is_full()

    def is_available(self) -> bool:
        cap = self.available_servers.capacity
        in_use = self.available_servers.count
        return in_use < cap

    def is_active(self) -> bool:
        return self.available_servers.count > 0

    def serve(self, visitor: Visitor, req: sp.Resource):
        pass

    def schedule(self):
        pass


class Reception(System):
    def __init__(
            self,
            env: sp.Environment,
            params: pr.SystemParams,
            queue_params: pr.QueueParams,
            server_params: pr.ServerParams,
            rooms: list[System] = None,
    ) -> None:
        self.rooms = rooms
        self.idle_proc = None
        self.active_proc = None
        self.is_idle = True
        super().__init__(env, params, queue_params, server_params)

    def set_rooms(self, rooms: list[System]):
        self.rooms = rooms
        return self

    def get_name(self) -> str:
        return self.params.name

    def serve(self, visitor: Visitor, req: sp.Resource):
        # MMN0208: Update service time
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
                    self.stats.update_service_requests()
                    visitor = self.find_visitor()
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
            # MMN0208: update idle_start, total_idle_count
            idle_start = self.env.now
            print(f"At time t = {idle_start}, Reception IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            # MMN0208: update idle_end, total_idle_time
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
        room = random.randint(1,4) 
        Room.add_visitor(room,visitor)
        return

    def run(self):
        self.env.process(self.schedule())


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
        super().__init__(env, params, queue_params, server_params)

    def set_hallway(self, hallway: System):
        self.hallway = hallway
        return self

    def add_visitor(self, visitor: Visitor):
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

    # Serve visitor for visting the room
    def serve(self, visitor: Visitor, req: sp.Resource):
        server = RoomServer(
            env=self.env,
            params=self.server_params,
        )
        yield from server.process(visitor=visitor)
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
                    self.stats.update_service_requests()
                    visitor = self.find_visitor()
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
            # MMN0208: update idle_start
            idle_start = self.env.now
            print(f"At time t = {idle_start}, Room IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            # MMN0208: update idle_end, total_idle_time
            idle_end = self.env.now
            print(f"At time t = {idle_end}, Room IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _move_to_hallway(self, visitor: Visitor):
        print(
            f"At time t = {self.env.now}, Room TO_HALLWAY visitor = {visitor.get_name()}")
        # Add this room to list of visited place of visitor
        # Move visitor to hallway
        # self.hallway
        # This room name: self.get_name()
        # visitor.visited(room) //Not sure should have this or not?
        visitor.visited(Room.get_name) # Fix it later.
        Hallway.add_visitor(self.hallway,visitor)
    def run(self):
        self.env.process(self.schedule())


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
        super().__init__(env, params, queue_params, server_params)

    def set_rooms(self, rooms: list[Room]):
        self.rooms = rooms
        return self

    def get_name(self) -> str:
        return self.params.name

    def add_visitor(self, visitor: Visitor):
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

    # Should be doing nothing
    def serve(self, visitor: Visitor, req: sp.Resource):
        return

    # Moves its visitor to rooms
    def schedule(self):
        while True:
            if not self.is_empty():
                visitor = self.find_visitor()
                where = self._find_unvisited_room(visitor=visitor)
                room = self.rooms[where]
                # Add visitor to that room
                self.stats.update_visitor_count()
                continue
            else:
                print(
                    f"At time t = {self.env.now}, Hallway NO_VISITOR start idle")
            idle_timeout = self._idle()
            self.idle_proc = self.env.process(idle_timeout)
            yield self.idle_proc
            
    def _idle(self):
        try:
            # MMN0208: update idle_start, total_idle_count
            idle_start = self.env.now
            print(f"At time t = {idle_start}, Hallway IDLE starts")
            yield self.env.timeout(pr.SIM_DURATION)
        except sp.Interrupt:
            # MMN0208: update idle_end, total_idle_time
            idle_end = self.env.now
            print(f"At time t = {idle_end}, Hallway IDLE ends")
            self.stats.update_idle_time(idle_time=idle_end - idle_start)

    def _find_unvisited_room(self, visitor: Visitor) -> int:
        # Find unvisited room and returns an index
        # self.rooms
        # This hallway name: self.get_name()
        return 0

    def run(self):
        self.env.process(self.schedule())

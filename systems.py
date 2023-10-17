import simpy as sp
import params as pr
from visitor import Visitor
from qs import Queue
from servers import ReceptionServer, RoomServer
from system_stats import SystemStatistics
import random
from base_systems import System, SystemScheduleResult

class Check:
    def __init__(self, env, name):
        self.env = env
        self.name = name

    def check(self, job):
        passed = np.random.choice([True, False], p=[0.8, 0.2])
        if passed:
            print(f"At time t = {self.env.now}, Check {self.name}: Job {job.name} passed the check.")
            return True
        else:
            print(f"At time t = {self.env.now}, Check {self.name}: Job {job.name} failed the check.")
            return False
        
class ProductionLineA:
    def __init__(self, env, max_queue_size, name, server, check):
        self.env = env
        self.max_queue_size = max_queue_size
        self.name = name
        self.server = server
        self.check = check
        self.jobs = []

    def add_job(self, job):
        if len(self.jobs) < self.max_queue_size:
            self.jobs.append(job)
            print(f"At time t = {self.env.now}, Production Line A: Job {job.name} added to the queue.")
        else:
            print(f"At time t = {self.env.now}, Production Line A cannot add job {job.name}.")

    def pop_job(self, job):
        if self.jobs:
            job = self.jobs.pop()
            print(f"At time t = {self.env.now}, Production Line A: Job {job.name} popped to the queue.")
            return job
        else:
            print(f"At time t = {self.env.now}, Production Line A cannot add job {job.name}.")

    def is_empty(self):
        return len(self.jobs) == 0

    def is_full(self):
        return len(self.jobs) >= self.max_queue_size

    def __len__(self):
        return len(self.jobs)

    def capacity(self):
        return self.max_queue_size
    
class ProductionLineB:
    def __init__(self, env, max_queue_size, name, server, check):
        self.env = env
        self.max_queue_size = max_queue_size
        self.name = name
        self.server = server
        self.check = check
        self.jobs = []

    def add_job(self, job):
        if len(self.jobs) < self.max_queue_size:
            self.jobs.append(job)
            print(f"At time t = {self.env.now}, Production Line A: Job {job.name} added to the queue.")
        else:
            print(f"At time t = {self.env.now}, Production Line A cannot add job {job.name}.")

    def pop_job(self, job):
        if self.jobs:
            job = self.jobs.pop()
            print(f"At time t = {self.env.now}, Production Line A: Job {job.name} popped to the queue.")
            return job
        else:
            print(f"At time t = {self.env.now}, Production Line A cannot add job {job.name}.")

    def is_empty(self):
        return len(self.jobs) == 0

    def is_full(self):
        return len(self.jobs) >= self.max_queue_size

    def __len__(self):
        return len(self.jobs)

    def capacity(self):
        return self.max_queue_size
    
class AdvancedProductionLine:
    def __init__(self, env, max_queue_size, name, server, check, production_lines):
        self.env = env
        self.max_queue_size = max_queue_size
        self.name = name
        self.server = server
        self.check = check
        self.production_lines = production_lines

    def add_job(self, job, line_index):
        if line_index < len(self.production_lines):
            line = self.production_lines[line_index]
            line.add_job(job)
        else:
            print(f"At time t = {self.env.now}, Advanced Production Line: Invalid line index.")

    def pop_job(self, line_index):
        if line_index < len(self.production_lines):
            line = self.production_lines[line_index]
            return line.pop_job()
        else:
            print(f"At time t = {self.env.now}, Advanced Production Line: Invalid line index.")
            return None

    def is_empty(self, line_index):
        if line_index < len(self.production_lines):
            line = self.production_lines[line_index]
            return line.is_empty()
        else:
            print(f"At time t = {self.env.now}, Advanced Production Line: Invalid line index.")
            return True

    def is_full(self, line_index):
        if line_index < len(self.production_lines):
            line = self.production_lines[line_index]
            return line.is_full()
        else:
            print(f"At time t = {self.env.now}, Advanced Production Line: Invalid line index.")
            return True

    def __len__(self, line_index):
        if line_index < len(self.production_lines):
            line = self.production_lines[line_index]
            return len(line)
        else:
            print(f"At time t = {self.env.now}, Advanced Production Line: Invalid line index.")
            return 0

    def capacity(self, line_index):
        if line_index < len(self.production_lines):
            line = self.production_lines[line_index]
            return line.capacity()
        else:
            print(f"At time t = {self.env.now}, Advanced Production Line: Invalid line index.")
            return 0

# class Room(System):
#     def __init__(
#             self,
#             env: sp.Environment,
#             params: SystemParams,
#             queue_params: QueueParams,
#             server_params: ServerParams,
#             hallway: System = None) -> None:
#         self.hallway = hallway
#         super().__init__(env, params, queue_params, server_params)

#     def set_hallway(self, hallway: System):
#         self.hallway = hallway
#         return self

#     # Moves visitor to hallway

#     def schedule(self):
#         while True:
#             res, visitor, req = self.request_server()
#             match res:
#                 case SystemScheduleResult.FOUND_VISITOR:
#                     server = RoomServer(
#                         env=self.env,
#                         params=self.server_params,
#                     )
#                     yield req
#                     self.env.process(self.serve(
#                         visitor=visitor, req=req, server=server))
#                     self._move_to_hallway(visitor=visitor)
#                 case _:
#                     if self.is_active():
#                         yield from self.go_active()
#                     else:
#                         yield from self.go_idle()

#     def _move_to_hallway(self, visitor: Visitor):
#         print(
#             f"At time t = {self.env.now}, Room TO_HALLWAY visitor = {visitor.get_name()}")
#         self.hallway.add_visitor(visitor=visitor)

#         visitor.visited(self)

#         self.hallway.add_visitor(visitor=visitor)

#     def run(self):
#         super().run()
#         self.env.process(self.schedule())


# class Hallway(System):
#     def __init__(
#             self,
#             env: sp.Environment,
#             params: SystemParams,
#             queue_params: QueueParams,
#             server_params: ServerParams,
#             rooms: list[Room] = None) -> None:
#         self.rooms = rooms
#         super().__init__(env, params, queue_params, server_params)

#     def set_rooms(self, rooms: list[System]):
#         self.rooms = rooms
#         return self

#     # Moves its visitor to rooms
#     def schedule(self):
#         while True:
#             res, visitor, req = self.request_server()
#             match res:
#                 case SystemScheduleResult.FOUND_VISITOR:
#                     server = HallwayServer(
#                         env=self.env,
#                         params=self.server_params,
#                     )
#                     yield req
#                     self.env.process(self.serve(
#                         visitor=visitor, req=req, server=server))
#                     self._send_to_unvisited_room(visitor=visitor)
#                 case _:
#                     if self.is_active():
#                         yield from self.go_active()
#                     else:
#                         yield from self.go_idle()

#     def _send_to_unvisited_room(self, visitor: Visitor) -> int:
#         # Find unvisited room and returns an index
#         # self.rooms
#         all_rooms = self.rooms
#         available_rooms = []
#         for i, r in enumerate(all_rooms):
#             if visitor.has_visited(r.get_name()):
#                 available_rooms.append(i)
#         if len(available_rooms) == 0:
#             print("Hallway VISITOR_DONE")
#             return
#         chosen = random.choice(available_rooms)
#         all_rooms[chosen].add_visitor(visitor=visitor)

#         for index, room in enumerate(self.rooms):
#             if not visitor.has_visited(room):
#                 return index

#         return -1

#     def run(self):
#         super().run()
#         self.env.process(self.schedule())


# class Reception(System):
#     def __init__(
#             self,
#             env: sp.Environment,
#             params: SystemParams,
#             queue_params: QueueParams,
#             server_params: ServerParams,
#             rooms: list[Room] = None,
#             hallway: Hallway = None
#     ) -> None:
#         self.rooms = rooms
#         self.hallway = hallway
#         super().__init__(env, params, queue_params, server_params)

#     def set_rooms(self, rooms: list[Room]):
#         self.rooms = rooms
#         return self

#     def set_hallway(self, hallway: Hallway):
#         self.hallway = hallway
#         return self

#     def schedule(self):
#         while True:
#             res, visitor, req = self.request_server()
#             match res:
#                 case SystemScheduleResult.FOUND_VISITOR:
#                     server = ReceptionServer(
#                         env=self.env,
#                         params=self.server_params,
#                     )
#                     yield req
#                     self.env.process(self.serve(
#                         visitor=visitor, req=req, server=server))
#                     self._move_to_room(visitor=visitor)
#                 case _:
#                     if self.is_active():
#                         yield from self.go_active()
#                     else:
#                         yield from self.go_idle()

#     # Move visitor to room
#     def _move_to_room(self, visitor: Visitor):
#         print(
#             f"At time t = {self.env.now}, Reception MOVE_TO_ROOM visitor = {visitor.get_name()}")

#         # Check which room available
#         avail_room: list[System] = []

#         for room in self.rooms:
#             if room.is_available() and not room.is_full():
#                 avail_room.append(room)

#         if len(avail_room) > 0:
#             room_select = random.choice(avail_room)
#             room_select.add_visitor(visitor=visitor)
#             return

#         self.hallway.add_visitor(visitor=visitor)
#         return

#     def run(self):
#         super().run()
#         self.env.process(self.schedule())

import simpy as sp
import params as pr
from visitor import Visitor
from qs import Queue
from servers import ProductionLineServer, DispatcherServer
from system_stats import SystemStatistics
import random
from base_systems import System, SystemScheduleResult


class Product:
    def __init__(self, name: str, processing_time: float):
        self.name = name
        self.processing_time = processing_time

    def get_name(self) -> str:
        return self.name

    def get_processing_time(self) -> float:
        return self.processing_time

class Dispatcher(System):
    def __init__(
            self,
            env: sp.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_line: ProductionLine = None) -> None:
        self.production_lines = production_lines
        super().__init__(env, params, queue_params, server_params)

    def set_production_line(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self


    def schedule(self):
        while True:
            res, product, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_SERVER:
                    server = DispatcherServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        product=product, req=req, server=server))
                    self._move_to_next_production_line(product=product)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    # Move visitor to room
    def _move_to_next_production_line(self, product: Product):
        print(
            f"At time t = {self.env.now}, Reception MOVE_TO_ROOM visitor = {product.get_name()}")
        
         if random.random() > product.get_success_rate():
            production_line = random.choice(self.production_lines[:2])
            production_line.add_product(product=product)
            return

        self.production_lines[2].add_product(product=product)
        return

    def run(self):
        super().run()
        self.env.process(self.schedule())

class ProductionLine(System):
    def __init__(
        self,
        env: sp.Environment,
        name: str,
        queue_params: pr.QueueParams,
        server_params: pr.ServerParams,
        qa_check: QACheck = None,
    ) -> None:
        super().__init__(env, name, queue_params, server_params)
        self.qa_check = qa_check

    def schedule(self):
        while True:
            visitor, request = self.request_server()
            if visitor is not None:
                if self.qa_check is not None:
                    self.qa_check.add_visitor(visitor=visitor)
                else:
                    visitor.is_complete = True

                self.server.release(request)

            else:
                yield self.env.timeout(0.25)

class QACheck(System):
    def __init__(
            self,
            env: simpy.Environment,
            params: SystemParams,
            queue_params: QueueParams,
            server_params: ServerParams,
            production_lines: list[ProductionLine],
            hallway: System = None) -> None:
        self.production_lines = production_lines
        super().__init__(env, params, queue_params, server_params)

    def set_production_lines(self, production_lines: list[ProductionLine]):
        self.production_lines = production_lines
        return self


    def schedule(self):
        while True:
            res, product, req = self.request_server()
            match res:
                case SystemScheduleResult.FOUND_SERVER:
                    server = QACheckServer(
                        env=self.env,
                        params=self.server_params,
                    )
                    yield req
                    self.env.process(self.serve(
                        product=product, req=req, server=server))
                    self._move_to_next_production_line(product=product)
                case _:
                    if self.is_active():
                        yield from self.go_active()
                    else:
                        yield from self.go_idle()

    def _move_to_next_production_line(self, product: Product):

        if random.random() > self.success_rate:
            product.is_complete = True
        else:
            # move_to_next_production_line
        return


    def run(self):
        super().run()
        self.env.process(self.schedule())

    


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

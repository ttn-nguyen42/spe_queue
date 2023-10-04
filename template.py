class Mediator:
    def __init__(self):
        self.room = None
        self.hallway = None
        self.reception = None

    def register_room(self, room):
        self.room = room

    def register_hallway(self, hallway):
        self.hallway = hallway
        
    def register_reception(self, reception):
        self.receptiion = reception

    def add_visitor_from_room_to_hallway(self, visitor name):
        self.hallway.add_visitor()

    def add_visitor_from_hallway_to_room(self, visitor name):
        self.room.add_visitor()
        
    def add_visitor_from_reception_to_room(self, visitor name):
        self.room.add_visitor()

class RoomServer(VisitorServer):
    def init(self, room_id, ServerParams, mediator):
        generate room_id 
        generate server
        self.mediator
        
    def add_visitor_to_hallway(self):
        self.mediator.add_visitor_from_room_to_hallway(visitor name)    
        
    def process:
        visit this room_id
        
    def stop:
        stop visit this room
        self.mediator.add_visitor()

class Room(System):
    def init(room_id, SystemParams, QueueParams,ServerParams, mediator):
        self.server = RoomServer(room_id, ServerParams, mediator)
        
    def serve:
        server.process(visitor name)
        
    def schedule():
        while there is visitor:
            if there is server:
                visitor.dequeue()
                serve(visitor name)
                
class HallWay(System):
    def init(ServerParams, meditor): # no service time, no interval time, no server,queue size infinite
        self.rooms = []
        self.mediator = mediator
        
    def add_visitor_to_room():
        self.mediator.add_visitor_from_hallway_to_room(visitor name)
        
    def schedule():
        while True:
            if queue is not empty:
                get_visitor #get_visitor not dequeue to check their visited_places
                for each room:
                    if visitor not visit this room:
                        if that room is not full:
                            self.mediator.add_visitor(room_id)
                            
        
room_map = list [room_id:
                 {
                    mean_service_time:
                    queue_size:
                    server_size:
                 }
                 ,
                 room_id:
                 {
                    mean_service_time:
                    queue_size:
                    server_size:
                 }
                 ...]


class Museum(System):
	def init(room_map):
        self.mediator = Mediator()
		self.reception = Reception(self.mediator)
		self.hallway = HallWay(self.mediator)
  		self.rooms = self.generate_room(room_map, self.mediator) -> list
    

	def generate_room(room_map: list, hallway: HallWay)
		room_list = []
		for i in range size of room_map:
			room_list[i] = Room(i, SystemParams, QueueParams,ServerParams)			
   
### Modifications on the newest one
class ReceptionServer:
    def process:
        for visitor has not visited this place:
            if room(room_id) is not full:
                visit_room(room_id)
                
    def add_visitor_to_room(self):
        self.mediator.add_visitor_from_reception_to_room(visitor name)   


Generator()
    add_visitor(Visitor(name, map))
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

    def add_visitor_from_room_to_hallway(self):
        self.hallway.add_visitor()

    def add_visitor_from_hallway_to_room(self):
        self.room.add_visitor()
        
    def add_visitor_from_reception_to_room(self):
        self.room.add_visitor()


class Room:
    def __init__(self, mediator):
        self.mediator = mediator

    def add_visitor(self):
        print("add visitor to room")

    def add_to_hallway(self):
        self.mediator.add_visitor_from_room_to_hallway()


class HallWay:
    def __init__(self, mediator):
        self.mediator = mediator

    def add_visitor(self):
        print("add visitor to hallway")

    def add_to_room(self):
        self.mediator.add_visitor_from_hallway_to_room()


def main():
    mediator = Mediator()
    room = Room(mediator)
    hallway = HallWay(mediator)

    mediator.register_room(room)
    mediator.register_hallway(hallway)

    # Call a method in HallWay that calls a method in Room
    hallway.add_to_room()

    # Call a method in Room that calls a method in HallWay
    room.add_to_hallway()


if __name__ == "__main__":
    main()
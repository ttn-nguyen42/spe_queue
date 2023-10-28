from product import Product
from typing import List
import params as pr


class Queue:
    """
    Hold visitors
    """

    def __init__(
        self,
        params: pr.QueueParams,
    ) -> None:
        self.visitors: List[Visitor] = []
        self.params = params
        return

    def enqueue(self, visitor: Visitor):
        if self.is_full():
            raise Exception("queue is full")
        self.visitors.append(visitor)

    def dequeue(self) -> Visitor:
        if self.is_empty():
            raise Exception("queue is empty")
        return self.visitors.pop(0)

    def is_empty(self):
        return len(self.visitors) == 0

    def is_full(self):
        return len(self.visitors) >= self.params.max_queue_size

    def __len__(self):
        return len(self.visitors)

    def capacity(self):
        return self.params.max_queue_size

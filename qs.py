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
        self.products: List[Products] = []
        self.params = params
        return

    def enqueue(self, product: Product):
        if self.is_full():
            raise Exception("queue is full")
        self.products.append(product)

    def dequeue(self) -> Product:
        if self.is_empty():
            raise Exception("queue is empty")
        return self.products.pop(0)

    def is_empty(self):
        return len(self.products) == 0

    def is_full(self):
        return len(self.products) >= self.params.max_queue_size

    def __len__(self):
        return len(self.products)

    def capacity(self):
        return self.params.max_queue_size

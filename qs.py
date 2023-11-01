from product import Product
from typing import List
import params as pr


class Queue:
    """
    Hold visitors
    """

    def __init__(
        self
    ) -> None:
        self.products: List[Product] = []
        return

    def enqueue(self, product: Product):
        self.products.append(product)

    def dequeue(self) -> Product:
        if self.is_empty():
            raise Exception("queue is empty")
        return self.products.pop(0)

    def is_empty(self):
        return len(self.products) == 0

    def __len__(self):
        return len(self.products)

from abc import ABC, abstractmethod

from ..entities import Order


class OrderRepository(ABC):
    @abstractmethod
    def create_pending_order(self, seat_id: int) -> Order:
        raise NotImplementedError

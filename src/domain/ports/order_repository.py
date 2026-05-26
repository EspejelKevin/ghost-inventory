from abc import ABC, abstractmethod

from ..entities import Order


class OrderRepository(ABC):
    @abstractmethod
    def create_pending_order(self, seat_id: int) -> Order:
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: int) -> Order | None:
        raise NotImplementedError
    
    @abstractmethod
    def save(self, order: Order) -> None:
        raise NotImplementedError

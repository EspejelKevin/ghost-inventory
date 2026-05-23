from abc import ABC, abstractmethod
from typing import Optional

from ..entities import Seat


class SeatRepository(ABC):
    @abstractmethod
    def get_seat_for_update(self, seat_id: int) -> Optional[Seat]:
        raise NotImplementedError
    
    @abstractmethod
    def save(self, seat: Seat) -> None:
        raise NotImplementedError

from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class SeatStatus(str, Enum):
    AVAILABLE = 'DISPONIBLE'
    RESERVED = 'RESERVADO'
    SOLD = 'VENDIDO'


class OrderStatus(str, Enum):
    PENDING = 'PENDIENTE'
    COMPLETED = 'COMPLETADA'
    EXPIRED = 'EXPIRADA'


@dataclass
class Seat:
    id: int
    status: SeatStatus

    def reserve(self):
        if self.status != SeatStatus.AVAILABLE:
            raise ValueError('El asiento ya no se encuentra disponible para reserva')
        self.status = SeatStatus.RESERVED

@dataclass
class Order:
    id: int
    seat_id: int
    status: OrderStatus
    created_at: datetime

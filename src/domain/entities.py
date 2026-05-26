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

    def sell(self):
        if self.status != SeatStatus.RESERVED:
            raise ValueError('Solo se pueden comprar asientos previamente reservados')
        self.status = SeatStatus.SOLD

@dataclass
class Order:
    id: int
    seat_id: int
    status: OrderStatus
    created_at: datetime

    def complete(self):
        if self.status != OrderStatus.PENDING:
            raise ValueError('La orden ya fue procesada o expiró')
        self.status = OrderStatus.COMPLETED

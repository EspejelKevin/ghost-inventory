from src.domain import SeatRepository, OrderRepository, OrderStatus


class ExpireReservationUseCase:
    def __init__(self, seat_repository: SeatRepository, order_repository: OrderRepository) -> None:
        self.seat_repository = seat_repository
        self.order_repository = order_repository

    def execute(self, seat_id: int, order_id: int) -> None:
        seat = self.seat_repository.get_seat_for_update(seat_id)
        order = self.order_repository.get_order(order_id)

        if not seat or not order:
            raise ValueError(f"Error: No se encontro el asiento {seat_id} o la orden {order_id}")
        
        if order.status == OrderStatus.PENDING:
            order.expire()
            seat.release()

            self.order_repository.save(order)
            self.seat_repository.save(seat)
            print(f"Expiracion completada: asiento {seat_id} liberado y orden {order_id} expirada")
        else:
            print(f"Expiracion ignorada: la orden {order_id} ya fue pagada o no está pendiente")

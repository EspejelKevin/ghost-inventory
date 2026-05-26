from src.domain import SeatRepository, OrderRepository, TaskScheduler


class ConfirmPaymentUseCase:
    def __init__(self, seat_repository: SeatRepository,
                 order_repository: OrderRepository, scheduler: TaskScheduler) -> None:
        self.seat_repository = seat_repository
        self.order_repository = order_repository
        self.scheduler = scheduler

    def execute(self, order_id: int) -> dict:
        order = self.order_repository.get_order(order_id)
        
        if not order:
            raise ValueError(f'La orden {order_id} no existe')
        
        seat = self.seat_repository.get_seat_for_update(order.seat_id)
        
        if not seat:
            raise ValueError(f'El asiento con id: {order.seat_id} no existe')

        order.complete()
        seat.sell()

        self.order_repository.save(order)
        self.seat_repository.save(seat)

        job_id = f'expire_seat_{seat.id}_order_{order.id}'
        self.scheduler.cancel_expiration(job_id)

        return {
            'order_id': order.id,
            'seat_id': seat.id,
            'status': order.status.value
        }

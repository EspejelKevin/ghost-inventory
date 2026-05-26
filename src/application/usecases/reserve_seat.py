import uuid

from datetime import datetime, timedelta, timezone

from src.domain import SeatRepository, OrderRepository, TaskScheduler


class ReserveSeatUseCase:
    def __init__(self, seat_repository: SeatRepository,
                 order_repository: OrderRepository, scheduler: TaskScheduler) -> None:
        self.seat_repository = seat_repository
        self.order_repository = order_repository
        self.scheduler = scheduler

    def execute(self, seat_id: int) -> dict:
        seat = self.seat_repository.get_seat_for_update(seat_id)

        if not seat:
            raise ValueError(f'El asiento con id: {seat_id} no existe')

        seat.reserve()
        self.seat_repository.save(seat)

        order = self.order_repository.create_pending_order(seat_id)
        
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)
        job_id = f'expire_seat_{seat_id}_order_{order.id}'
        print(f'Job {job_id}')

        self.scheduler.schedule_expiration(job_id, expires_at, seat_id, order.id)

        return {
            'reservation_id': order.id,
            'expires_at': expires_at.isoformat()
        }

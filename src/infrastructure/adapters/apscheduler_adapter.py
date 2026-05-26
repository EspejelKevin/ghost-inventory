from apscheduler.schedulers.base import BaseScheduler

from datetime import datetime

from src.domain import TaskScheduler
from src.application import ExpireReservationUseCase
from ..database.connection import SessionLocal
from .repositories.postgres_order_repository import PostgresOrderRepository
from .repositories.postgres_seat_repository import PostgresSeatRepository


def expire_reservation_task(seat_id: int, order_id: int) -> None:
    print(f'Ejecutando worker de expiracion para asiento: {seat_id}, Order: {order_id}')

    session = SessionLocal()
    try:
        seat_repository = PostgresSeatRepository(session)
        order_repository = PostgresOrderRepository(session)
        usecase = ExpireReservationUseCase(seat_repository, order_repository)

        usecase.execute(seat_id, order_id)

    except Exception as e:
        session.rollback()
        print(f'Error en worker de expiracion: {e}')
    finally:
        session.close()


class APSchedulerAdapter(TaskScheduler):
    def __init__(self, scheduler: BaseScheduler) -> None:
        self.scheduler = scheduler

    def schedule_expiration(self, job_id: str, run_date: datetime, seat_id: int, order_id: int) -> None:
        self.scheduler.add_job(
            func=expire_reservation_task,
            trigger='date',
            run_date=run_date,
            args=[seat_id, order_id],
            id=job_id,
            replace_existing=True,
            misfire_grace_time=300
        )

    def cancel_expiration(self, job_id: str) -> None:
        try:
            self.scheduler.remove_job(job_id)
            print(f"Job {job_id} cancelado exitosamente. Boleto pagado")
        except Exception:
            pass

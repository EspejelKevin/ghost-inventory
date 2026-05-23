from apscheduler.schedulers.base import BaseScheduler

from datetime import datetime

from src.domain import TaskScheduler


def expire_reservation_task(seat_id: int, order_id: int) -> None:
    print(f'Ejecutando worker de expiracion para asiento: {seat_id}, Order: {order_id}')


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

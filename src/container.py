from dependency_injector import containers, providers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from src.infrastructure import PostgresSeatRepository, PostgresOrderRepository, APSchedulerAdapter, get_db_session
from src.application import ReserveSeatUseCase, ConfirmPaymentUseCase


def init_apscheduler() -> AsyncIOScheduler:
    jobstores = {
        'default': RedisJobStore(host='localhost', port=6379, db=0)
    }
    return AsyncIOScheduler(jobstores=jobstores)


class Container(containers.DeclarativeContainer):
    db_session = providers.Resource(get_db_session)

    scheduler = providers.Singleton(init_apscheduler)

    seat_repository = providers.Factory(
        PostgresSeatRepository,
        session=db_session
    )

    order_repository = providers.Factory(
        PostgresOrderRepository,
        session=db_session
    )

    task_scheduler = providers.Factory(
        APSchedulerAdapter,
        scheduler=scheduler
    )

    reserve_seat_usecase = providers.Factory(
        ReserveSeatUseCase,
        seat_repository=seat_repository,
        order_repository=order_repository,
        scheduler=task_scheduler
    )

    confirm_payment_usecase = providers.Factory(
        ConfirmPaymentUseCase,
        seat_repository=seat_repository,
        order_repository=order_repository,
        scheduler=task_scheduler
    )

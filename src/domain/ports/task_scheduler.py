from abc import ABC, abstractmethod
from datetime import datetime


class TaskScheduler(ABC):
    @abstractmethod
    def schedule_expiration(self, job_id: str, run_date: datetime, seat_id: int, order_id: int) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def cancel_expiration(self, job_id: str) -> None:
        raise NotImplementedError

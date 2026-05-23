from sqlalchemy.orm import Session

from domain import SeatRepository, Seat, SeatStatus
from ...models.seat import SeatModel


class PostgresSeatRepository(SeatRepository):
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def get_seat_for_update(self, seat_id: int) -> Seat | None:
        seat_orm = self.session.query(SeatModel).filter_by(id=seat_id).with_for_update().first()
        if not seat_orm:
            return None
        return Seat(id=seat_orm.id, status=SeatStatus(seat_orm.status))

    def save(self, seat: Seat) -> None:
        seat_orm = self.session.query(SeatModel).filter_by(id=seat.id).first()
        if seat_orm:
            seat_orm.status = seat.status.value
            self.session.commit()

from sqlalchemy.orm import Session

from domain import OrderRepository, Order, OrderStatus


class PostgresOrderRepository(OrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_pending_order(self, seat_id: int) -> Order:
        new_order = OrderModel(seat_id=seat_id, status=OrderStatus.PENDING.value)
        self.session.add(new_order)
        self.session.commit()
        self.session.refresh(new_order)

        return Order(
            id=new_order.id,
            seat_id=new_order.seat_id,
            status=OrderStatus(new_order.status),
            created_at=new_order.created_at
        )

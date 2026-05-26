from sqlalchemy.orm import Session

from src.domain import OrderRepository, Order, OrderStatus
from ...models.order import OrderModel


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
    
    def get_order(self, order_id: int) -> Order | None:
        order_orm = self.session.query(OrderModel).filter_by(id=order_id).first()
        
        if not order_orm:
            return None
        
        return Order(
            id=order_orm.id,
            seat_id=order_orm.seat_id,
            status=OrderStatus(order_orm.status),
            created_at=order_orm.created_at
        )
    
    def save(self, order: Order) -> None:
        order_orm = self.session.query(OrderModel).filter_by(id=order.id).first()
        
        if order_orm:
            order_orm.status = order.status.value
            self.session.commit()

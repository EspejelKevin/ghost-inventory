from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from datetime import datetime

from ..database.connection import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seat_id: Mapped[int] = mapped_column(Integer, ForeignKey("seats.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDIENTE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    seat = relationship("SeatModel", back_populates="orders")

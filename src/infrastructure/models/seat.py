from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from ..database.connection import Base


class SeatModel(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="DISPONIBLE")
    orders = relationship("OrderModel", back_populates="seat")

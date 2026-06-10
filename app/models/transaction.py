"""Modelo ORM: Transaccion."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import EstadoTransaccion


class Transaction(Base):
    """Transaction Model."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    commerce_id: Mapped[int] = mapped_column(
        ForeignKey("commerces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reference: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="COP", nullable=False)
    # native_enum=False -> se persiste como VARCHAR (portable entre MariaDB y SQLite).
    status: Mapped[EstadoTransaccion] = mapped_column(
        SAEnum(EstadoTransaccion, native_enum=False, length=20),
        default=EstadoTransaccion.PENDIENTE,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    commerce: Mapped["Commerce"] = relationship(  # noqa: F821
        back_populates="transactions"
    )

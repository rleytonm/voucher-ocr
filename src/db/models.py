# src/db/models.py

from sqlalchemy import Column, Integer, String, Date, Numeric
from .connection import Base

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    monto = Column(Numeric(8, 2), nullable=False)
    fecha = Column(Date, nullable=False)
    banco_destino = Column(String(10), nullable=True)
    movimiento_id = Column(String(10), unique=False, nullable=False)

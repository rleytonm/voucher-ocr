#!/usr/bin/env python
import os, sys

# scripts/insert_test.py

#Añadir directorio padre al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from datetime import date
from src.db.connection import engine, SessionLocal, Base
from src.db.models import Pago

def main():
    # 1. Asegúrate de que las tablas existen
    Base.metadata.create_all(bind=engine)

    # 2. Abrimos sesión
    session = SessionLocal()
    try:
        # 3. Creamos un pago de prueba
        nuevo_pago = Pago(
            monto=500.00,
            fecha=date.today(),
            banco_destino="BCP",
            movimiento_id="TEST-0001"
        )
        session.add(nuevo_pago)
        session.commit()
        print(f"Inserción OK: id={nuevo_pago.id}")

        # 4. Consulta ese pago
        pago = session.query(Pago).filter_by(movimiento_id="TEST-0001").first()
        if pago:
            print("Consulta OK:", {
                "id": pago.id,
                "monto": float(pago.monto),
                "fecha": pago.fecha.isoformat(),
                "banco_destino": pago.banco_destino,
                "movimiento_id": pago.movimiento_id
            })
        else:
            print("No se encontró el pago de prueba.")
    finally:
        session.close()

if __name__ == "__main__":
    main()

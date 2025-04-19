#!/usr/bin/env python
# src/ocr/process.py

import os
import sys
import re
from datetime import date
from dotenv import load_dotenv
import cv2
import pytesseract
import dateparser
from dateparser.search import search_dates

# Configurar entorno
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
dotenv_path = os.path.join(project_root, 'config', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Asegurar imports del proyecto
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from src.db.connection import SessionLocal
from src.db.models import Pago

# --- Funciones de preprocesamiento y OCR ---

def preprocess_image(image_path: str):
    """Cargar imagen, mejorar contraste y binarizar para OCR."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {image_path}")
    # Aumentar resolución
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Reducir ruido
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    # Umbral adaptativo inverso
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 9
    )
    # Morfología para cerrar espacios
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # Invertir para OCR
    return cv2.bitwise_not(clean)


def ocr_extract(img, whitelist: str = None) -> str:
    """Extrae texto de imagen con Tesseract, opcional whitelist de caracteres."""
    config = "--oem 3 --psm 6"
    if whitelist:
        config += f" -c tessedit_char_whitelist={whitelist}"
    return pytesseract.image_to_string(img, lang='spa', config=config)

# --- Auxiliares de parseo ---

def normalize_amount(s: str) -> float:
    s = s.replace('O', '0').replace('l', '1')
    if ',' in s and '.' in s:
        # Comprobamos posición de separadores
        if s.rfind(',') < s.rfind('.'):
            s = s.replace(',', '')
        else:
            s = s.replace('.', '').replace(',', '.')
    elif s.count('.') > 1:
        intp, decp = s.rsplit('.', 1)
        s = intp.replace('.', '') + '.' + decp
    elif ',' in s:
        parts = s.split(',')
        if len(parts[1]) == 3:
            s = ''.join(parts)
        else:
            s = parts[0] + '.' + parts[1]
    return float(s)


def parse_movimiento(text: str) -> str:
    m = re.search(r"operaci[oó]n[:\s]*([0-9]{5,})", text, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    nums = re.findall(r"\d{5,}", text)
    return nums[-1] if nums else None

# --- Gestión de plantillas ---

template_registry = []

def register_template(name, detect_fn, parse_fn):
    template_registry.append({'name': name, 'detect': detect_fn, 'parse': parse_fn})


def detect_template(text: str):
    for tpl in template_registry:
        if tpl['detect'](text):
            return tpl
    return None

# --- Ejemplo de plantilla BCP ---

def detect_bcp(text: str) -> bool:
    return bool(re.search(r"Banco de Cr[eé]dito|\bBCP\b", text, flags=re.IGNORECASE))


def parse_bcp(text: str, img) -> dict:
    data = {}
    # Monto
    monto_text = ocr_extract(img, whitelist="0123456789,.")
    m = re.search(r"([0-9.,]+)", monto_text)
    data['monto'] = normalize_amount(m.group(1)) if m else None
    # Fecha
    dates = search_dates(text, languages=['es'], settings={'DATE_ORDER': 'DMY'})
    data['fecha'] = dates[0][1].date() if dates else None
    # Movimiento
    data['movimiento'] = parse_movimiento(text)
    # Banco
    data['banco'] = 'BCP'
    return data

# Registrar plantillas
default_templates = [
    ('BCP', detect_bcp, parse_bcp),
]
for name, det, par in default_templates:
    register_template(name, det, par)

# --- Parseador principal ---

def parse_fields(text: str, img) -> dict:
    tpl = detect_template(text)
    if tpl:
        return tpl['parse'](text, img)
    # Fallback genérico
    data = {'monto': None, 'fecha': None, 'movimiento': None, 'banco': None}
    # Monto
    m = re.search(r"S/\s*([0-9.,]+)", text)
    if m:
        data['monto'] = normalize_amount(m.group(1))
    # Fecha
    dates = search_dates(text, languages=['es'], settings={'DATE_ORDER': 'DMY'})
    if dates:
        data['fecha'] = dates[0][1].date()
    # Movimiento
    data['movimiento'] = parse_movimiento(text)
    return data

# --- Inserción en BD ---

def save_pago(data: dict) -> int:
    missing = [k for k in ('monto', 'fecha', 'movimiento') if not data.get(k)]
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {missing}")
    session = SessionLocal()
    try:
        pago = Pago(
            monto=data['monto'],
            fecha=data['fecha'],
            banco_destino=data.get('banco'),
            movimiento_id=data['movimiento']
        )
        session.add(pago)
        session.commit()
        return pago.id
    finally:
        session.close()

# --- Flujo de ejecución ---

def process_file(image_path: str):
    img_pre = preprocess_image(image_path)
    text = ocr_extract(img_pre)
    print("=== TEXTO OCR ===\n", text)
    data = parse_fields(text, img_pre)
    print("Campos parseados:", data)
    pid = save_pago(data)
    print(f"✅ Pago insertado con id {pid}")
    return data

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python src/ocr/process.py ruta/a/comprobante.jpg")
        sys.exit(1)
    try:
        process_file(sys.argv[1])
    except Exception as e:
        print(f"Error en procesamiento: {e}")
        sys.exit(1)

# Voucher OCR – Automated Payment Voucher Data Extraction
Overview

Voucher OCR is a Python-based image recognition system that extracts key information (dates, voucher numbers, payment amounts) from scanned payment vouchers and automatically stores the results in a database.

The goal is to reduce manual data entry, improve accuracy, and streamline financial document processing.

Problem

Processing payment vouchers manually is time-consuming and prone to human error. This project automates:

- Text recognition from voucher images (OCR)
- Extraction of structured financial data
- Automatic database insertion

How It Works

- A voucher image is provided as input.
- The image is processed and text is extracted using OCR.
- Relevant fields (date, numeric identifiers, amounts) are parsed.
- The extracted data is validated and inserted into a database.

Tech Stack: Python, OCR engine (Pytesseract), Image processing libraries, Database integration (SQLite or similar)

Installation

git clone https://github.com/rleytonm/voucher-ocr.git

cd voucher-ocr

pip install -r requirements.txt

Usage

Run the main script to process voucher images:

python main.py

Extracted information will be saved automatically to the configured database.

Example Extracted Fields:

- Voucher Date
- Voucher Number
- Payment Amount

Project Structure

voucher-ocr/
├── main.py
├── database.py
├── requirements.txt
└── README.md

Future Improvements

- Improve OCR accuracy with advanced preprocessing
- Support multiple voucher formats
- Add a web-based upload interface
- Implement automated testing

Author:
Cristian Renato Leyton Medina


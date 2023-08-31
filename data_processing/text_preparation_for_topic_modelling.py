# -*- coding: utf-8 -*-

"""
wymagane pakiety dodatkowe: pip install PyPDF2 tabula-py
"""
from PyPDF2 import PdfReader
import tabula
import json
from concurrent.futures import ProcessPoolExecutor
import os

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf_reader = PdfReader(f)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_tables_from_pdf(pdf_path, pages='all'):
    tables = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True)
    return [table.to_json(orient='split') for table in tables]

def process_single_pdf(pdf_path, output_folder):
    print(f"Processing {pdf_path}")

    text = extract_text_from_pdf(pdf_path)
    tables = extract_tables_from_pdf(pdf_path)

    output_data = {
        'text': text,
        'tables': tables
    }

    output_json_path = os.path.join(output_folder, f"{os.path.basename(pdf_path)}.json")

    with open(output_json_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

def main(pdf_folder, output_folder):
    pdf_files = [os.path.join(pdf_folder, filename) for filename in os.listdir(pdf_folder) if filename.endswith('.pdf')]

    os.makedirs(output_folder, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        executor.map(process_single_pdf, pdf_files, [output_folder]*len(pdf_files))

if __name__ == '__main__':
    pdf_folder = 'pdfy/'
    output_folder = 'outputy/'
    main(pdf_folder, output_folder)

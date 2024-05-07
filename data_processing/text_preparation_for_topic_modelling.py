import os
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
import layoutparser as lp
import tabula

model = lp.AutoLayoutModel('lp://EfficientDete/PubLayNet')

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list: List of text blocks extracted from the PDF.
    """
    try:
        layout = lp.load_pdf(pdf_path)
        blocks = []
        for l in layout:
            text = ''
            for block in l._blocks:
                text += block.text
                text += ' '
            blocks.append(text)
        logger.info(f'Extracted text from {pdf_path} with {len(blocks)} blocks')
        return blocks
    except Exception as e:
        logger.error(f'Error extracting text from {pdf_path}: {e}')
        return []

def extract_tables_from_pdf(pdf_path, pages='all'):
    """
    Extracts tables from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.
        pages (str, optional): Page numbers to extract tables from. Defaults to 'all'.

    Returns:
        list: List of dictionaries representing tables extracted from the PDF.
    """
    try:
        tables = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True)
        logger.info(f'Extracted {len(tables)} tables from {pdf_path}')
        return [table.to_json(orient='split') for table in tables]
    except Exception as e:
        logger.error(f'Error extracting tables from {pdf_path}: {e}')
        return []

def process_single_pdf(pdf_path, output_folder):
    """
    Process a single PDF file by extracting text and tables and saving the output to JSON.

    Args:
        pdf_path (str): Path to the PDF file to process.
        output_folder (str): Path to the output folder.
    """
    try:
        logger.info(f'Processing {pdf_path}')

        text = extract_text_from_pdf(pdf_path)
        tables = extract_tables_from_pdf(pdf_path)

        output_data = {
            'text': text,
            'tables': tables
        }

        output_json_path = os.path.join(output_folder, f"{os.path.basename(pdf_path).strip('.pdf')}.json")
        logger.info(f'Saving output to {output_json_path}')

        with open(output_json_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)
    except Exception as e:
        logger.error(f'Error while processing {pdf_path}: {e}')

def main(pdf_folder, output_folder):
    """
    Process all PDF files in a folder concurrently.

    Args:
        pdf_folder (str): Path to the folder containing PDF files.
        output_folder (str): Path to the output folder.
    """
    pdf_files = [os.path.join(pdf_folder, filename) for filename in os.listdir(pdf_folder) if filename.endswith('.pdf')]

    os.makedirs(output_folder, exist_ok=True)

    with ThreadPoolExecutor() as executor:
        executor.map(process_single_pdf, pdf_files, [output_folder]*len(pdf_files))

# Tests could be written here to validate the functionality of each function.

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process PDF files.')
    parser.add_argument('input_folder', help='Path to the folder containing PDF files')
    parser.add_argument('output_folder', help='Path to the output folder')
    args = parser.parse_args()

    main(args.input_folder, args.output_folder)

from typing import List
import PyPDF2
from pypdf import PdfReader
import typer
import pathlib

def get_files(dir: str) -> List[str]:
    """Get all files in a directory."""
    files = []
    for path in pathlib.Path(dir).rglob("*"):
        if path.is_file():
            files.append(str(path))
    return files


def check_if_real_pdf(file: str) -> bool:
    """Check if a file is a real pdf."""
    try:
        pdfFileObj = open(file, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        
    except Exception as e:
        print(e)
        with open("results/pdf_file_error.txt", "a") as f:
            f.write(file + "\n")


def check_if_has_digital_layer(file: str) -> bool:
    """Chceck if first 10 pages have text"""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            if len(text) > 1000:
                return True
        with open("results/pdf_digital_error.txt", "a") as f:
            f.write(file + "\n")
    except Exception as e:
        print(e)
        with open("results/pdf_digital_error.txt", "a") as f:
            f.write(file + "\n")


def main(dir: str):
    files = get_files(dir)
    for i, file in enumerate(files):
        print(f"Processing file {i+1}/{len(files)}")
        check_if_real_pdf(file)

        # chceck if file exists
        if not pathlib.Path("results/pdf_file_error.txt").exists():
            continue
        else:
            with open("results/pdf_file_error.txt", "r") as f:
                error_files = f.read().splitlines()
                if file in error_files:
                    continue

        check_if_has_digital_layer(file)


if __name__ == "__main__":
    typer.run(main)
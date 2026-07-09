"""core/file_loader.py — Load any supported file into a pandas DataFrame."""

import os
import pandas as pd
import pdfplumber
from app.core.exceptions import FileError


def load_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(file_path, encoding="utf-8-sig")
        elif ext in (".xlsx", ".xls"):
            return pd.read_excel(file_path)
        elif ext == ".json":
            return pd.read_json(file_path)
        elif ext == ".parquet":
            return pd.read_parquet(file_path)
        else:
            raise FileError(f"Unsupported file type: {ext}")
    except FileError:
        raise
    except Exception as e:
        raise FileError(f"Could not read file: {e}")


def extract_pdf_text(file_path: str) -> str:
    chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def extract_txt_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def is_structured(file_path: str) -> bool:
    return os.path.splitext(file_path)[1].lower() in (".csv", ".xlsx", ".xls", ".json", ".parquet")

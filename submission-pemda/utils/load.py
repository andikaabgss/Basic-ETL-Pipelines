import os
from typing import Any

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy import create_engine


def to_dataframe(data: Any) -> pd.DataFrame:
    """Konversi data menjadi pandas DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, list):
        return pd.DataFrame(data)
    if isinstance(data, dict):
        return pd.DataFrame([data])
    raise TypeError("Data harus berupa pandas.DataFrame, list of dict, atau dict")


def load_to_csv(data: Any, file_path: str = "output.csv") -> None:
    """Simpan data ke file CSV."""
    df = to_dataframe(data)
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    df.to_csv(file_path, index=False)
    print(f"[INFO] Data berhasil disimpan ke CSV: {file_path}")


def load_to_postgres(data: Any, db_url: str = None, table_name: str = "products", if_exists: str = "replace") -> None:
    """Simpan data ke database PostgreSQL."""
    df = to_dataframe(data)

    if db_url is None:
        db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL tidak ditemukan. Tetapkan DATABASE_URL di environment atau lewat parameter.")

    engine = create_engine(db_url)
    df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
    print(f"[INFO] Data berhasil disimpan ke PostgreSQL: {table_name}")


def load_to_sheet(data: Any, spreadsheet_id: str, range_name: str, credentials_file: str = "google-sheets-api.json") -> None:
    """Simpan data ke Google Sheets."""
    df = to_dataframe(data)
    if df.empty:
        print("[WARN] DataFrame kosong, tidak ada yang diupload ke Google Sheets")
        return

    if not spreadsheet_id:
        raise ValueError("Spreadsheet ID harus ditetapkan.")

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    values = [df.columns.tolist()] + df.fillna("").values.tolist()
    body = {"values": values}

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body,
    ).execute()

    print("[INFO] Data berhasil disimpan ke Google Sheets")
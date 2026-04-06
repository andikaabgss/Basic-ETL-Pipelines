import os

from dotenv import load_dotenv
from utils.extract import extract_all
from utils.load import load_to_csv, load_to_postgres, load_to_sheet
from utils.transform import transform_data

load_dotenv()


BASE_URL = os.getenv("BASE_URL", "https://fashion-studio.dicoding.dev/")
SPREADSHEET_ID = "1bDdqwI7WK4qunL7yhyzYadDgfkaVn-DfFj2aMrn8m3o"
SHEET_RANGE = "Sheet1!A2"
CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "google-sheets-api.json")

def build_db_url():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")

    if user and password and database:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    return None

# Temporary: Set DATABASE_URL for testing (remove after setup)
os.environ["DATABASE_URL"] = "postgresql://developer:supersecretpassword@localhost:5432/pemda"

def main() -> None:
    raw_data = extract_all(BASE_URL, max_pages=50)
    df = transform_data(raw_data)
    print(df.head())

    load_to_csv(df, 'product_fashion.csv')

    db_url = build_db_url()

    if db_url:
        load_to_postgres(df, db_url=db_url, table_name="products", if_exists="replace")
    else:
        postgres_vars = ["DATABASE_URL", "DB_USER", "DB_PASSWORD", "DB_NAME"]
        if any(os.getenv(var) for var in postgres_vars):
            print("[WARN] Konfigurasi PostgreSQL tidak lengkap, melewati load_to_postgres")
        else:
            print("[INFO] PostgreSQL tidak dikonfigurasi, melewati load_to_postgres")

    if SPREADSHEET_ID:
        load_to_sheet(df, spreadsheet_id=SPREADSHEET_ID, range_name=SHEET_RANGE, credentials_file=CREDENTIALS_FILE)


if __name__ == "__main__":
    main()

import re
from typing import Any, Dict, List, Optional, Union

import pandas as pd


def clean_price(price: Any) -> Optional[float]:
    """Normalize harga dan konversi USD ke IDR jika diperlukan."""
    if price is None or pd.isna(price):
        return None

    text = str(price).strip()
    if not text:
        return None

    is_usd = bool(re.search(r"\$|USD", text, flags=re.I))
    cleaned = re.sub(r"(?i)(rp|idr|usd|\$)", "", text)
    cleaned = cleaned.replace(",", "").replace(" ", "")

    match = re.search(r"\d+(?:\.\d+)?", cleaned)
    if not match:
        return None

    value = float(match.group(0))
    if is_usd:
        value *= 16000

    return value


def clean_rating(rating: Any) -> Optional[float]:
    """Extract numeric rating dari teks."""
    if rating is None or pd.isna(rating):
        return None

    text = str(rating)
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def clean_colors(colors: Any) -> Optional[int]:
    """Extract jumlah warna dari teks."""
    if colors is None or pd.isna(colors):
        return None

    text = str(colors)
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def clean_size(size: Any) -> Optional[str]:
    """Normalize size field dengan menghapus prefix 'Size:'."""
    if size is None or pd.isna(size):
        return None

    text = str(size).strip()
    text = re.sub(r"(?i)^size\s*:?\s*", "", text)
    return text if text else None


def clean_gender(gender: Any) -> Optional[str]:
    """Normalize gender field dengan menghapus prefix 'Gender:'."""
    if gender is None or pd.isna(gender):
        return None

    text = str(gender).strip()
    text = re.sub(r"(?i)^gender\s*:?\s*", "", text)
    return text if text else None


def transform_data(data: Union[List[Dict[str, Any]], pd.DataFrame]) -> pd.DataFrame:
    """Transformasi data mentah menjadi DataFrame bersih."""
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    expected_columns = ["title", "price", "rating", "size", "gender", "colors"]
    for column in expected_columns:
        if column not in df.columns:
            df[column] = None

    if df.empty:
        return df[expected_columns].copy()

    df["title"] = df["title"].astype(str).str.strip()
    df["price"] = df["price"].apply(clean_price)
    df["rating"] = df["rating"].apply(clean_rating)
    df["colors"] = df["colors"].apply(clean_colors)
    df["size"] = df["size"].apply(clean_size)
    df["gender"] = df["gender"].apply(clean_gender)

    df = df.dropna(subset=["title", "price"])

    before_filter = len(df)
    df = df[~df["title"].str.lower().str.contains(r"unknown product", na=False)]
    after_filter = len(df)
    if before_filter > after_filter:
        print(f"  Menghapus {before_filter - after_filter} produk dengan title 'unknown product'")

    before_duplicates = len(df)
    df = df.drop_duplicates(subset=["title", "price"])
    after_duplicates = len(df)
    if before_duplicates > after_duplicates:
        print(f"  Menghapus {before_duplicates - after_duplicates} duplikat produk")

    return df.reset_index(drop=True)
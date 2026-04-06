import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3


def fetch_page(url: str, timeout: int = DEFAULT_TIMEOUT, retries: int = DEFAULT_RETRIES) -> str:
    """Ambil HTML dari URL menggunakan requests dengan retry sederhana."""
    headers = {"User-Agent": USER_AGENT}
    last_exception: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_exception = exc
            if attempt < retries:
                print(f"[WARN] Gagal mengambil halaman {url} (attempt {attempt}), retrying...")
                time.sleep(attempt)
            else:
                print(f"[ERROR] Gagal mengambil halaman {url}: {exc}")

    return ""


def _clean_label_value(text: str, label: str) -> str:
    """Hapus prefix label jika ada dalam teks."""
    if not text:
        return ""

    text = text.strip()
    pattern = re.compile(rf"^{re.escape(label)}\s*:?\s*", flags=re.I)
    return pattern.sub("", text).strip()


def parse_product_item(item: Any) -> Dict[str, Any]:
    """Parse satu item produk dari elemen BeautifulSoup."""
    title = None
    price = None
    rating = None
    gender = None
    colors = None
    size = None

    title_tag = item.find("h3", class_="product-title") or item.find("h3")
    if title_tag:
        title = title_tag.get_text(strip=True)

    price_tag = item.find("span", class_="price") or item.find("p", class_="price")
    if price_tag:
        price = price_tag.get_text(strip=True)
    else:
        raw_price = item.find(text=re.compile(r"\$|Rp|IDR", flags=re.I))
        if raw_price:
            price = str(raw_price).strip()

    for desc in item.find_all(["p", "li", "span", "div"]):
        text = desc.get_text(strip=True)
        if not text:
            continue

        normalized = text.lower()
        if normalized.startswith("rating"):
            rating = _clean_label_value(text, "Rating")
        elif normalized.startswith("gender"):
            gender = _clean_label_value(text, "Gender")
        elif "color" in normalized:
            colors = _clean_label_value(text, "Colors")
        elif normalized.startswith("size"):
            size = _clean_label_value(text, "Size")

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "gender": gender,
        "colors": colors,
        "size": size,
        "timestamp": datetime.now().isoformat(),
    }


def extract_data(url: str) -> List[Dict[str, Any]]:
    """Ekstrak data dari 1 halaman URL."""
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("div", class_="product-details")

    if not items:
        print(f"Warning: Tidak ditemukan produk di {url}")

    products = []
    for index, item in enumerate(items, start=1):
        try:
            product = parse_product_item(item)
            if product["title"]:
                products.append(product)
            else:
                print(f"Warning: Produk ke-{index} tidak memiliki title, dilewati")
        except Exception as exc:
            print(f"Error parsing item ke-{index}: {exc}")

    return products


def extract_all(base_url: str, max_pages: int = 50) -> List[Dict[str, Any]]:
    """Ekstrak produk dari banyak halaman."""
    base_url = base_url if base_url.endswith("/") else f"{base_url}/"
    all_data: List[Dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        page_url = base_url if page == 1 else f"{base_url}page{page}/"
        print(f"Scraping page {page}: {page_url}")

        page_data = extract_data(page_url)
        if not page_data:
            print(f"No data found on page {page}, stopping...")
            break

        all_data.extend(page_data)
        if page < max_pages:
            time.sleep(1)

    print(f"Total produk yang berhasil diekstrak: {len(all_data)}")
    return all_data
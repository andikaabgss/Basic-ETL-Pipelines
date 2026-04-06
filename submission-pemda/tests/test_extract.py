import pytest
import requests
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from datetime import datetime

from utils.extract import (
    extract_data,
    extract_all
)

class TestExtractData:
    """Test cases untuk fungsi extract_data"""

    @patch('utils.extract.fetch_page')
    def test_extract_data_success(self, mock_fetch):
        """Test extract_data dengan data valid"""
        mock_html = """
        <html>
        <body>
            <div class="product-details">
                <h3 class="product-title">Product 1</h3>
                <span class="price">$10.00</span>
            </div>
            <div class="product-details">
                <h3 class="product-title">Product 2</h3>
                <span class="price">$20.00</span>
            </div>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = extract_data("https://example.com")

        assert len(result) == 2
        assert result[0]['title'] == "Product 1"
        assert result[0]['price'] == "$10.00"
        assert result[1]['title'] == "Product 2"
        assert result[1]['price'] == "$20.00"

    @patch('utils.extract.fetch_page')
    def test_extract_data_empty_html(self, mock_fetch):
        """Test extract_data dengan HTML kosong"""
        mock_fetch.return_value = ""

        result = extract_data("https://example.com")

        assert result == []

    @patch('utils.extract.fetch_page')
    def test_extract_data_no_products(self, mock_fetch):
        """Test extract_data dengan HTML tanpa produk"""
        mock_html = """
        <html>
        <body>
            <div class="some-other-class">
                <h3>Not a product</h3>
            </div>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = extract_data("https://example.com")

        assert result == []

    @patch('utils.extract.fetch_page')
    def test_extract_data_products_without_title(self, mock_fetch):
        """Test extract_data dengan produk tanpa title (harus difilter)"""
        mock_html = """
        <html>
        <body>
            <div class="product-details">
                <span class="price">$10.00</span>
            </div>
            <div class="product-details">
                <h3 class="product-title">Valid Product</h3>
                <span class="price">$20.00</span>
            </div>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = extract_data("https://example.com")

        assert len(result) == 1
        assert result[0]['title'] == "Valid Product"


class TestExtractAll:
    """Test cases untuk fungsi extract_all"""

    @patch('utils.extract.extract_data')
    @patch('time.sleep')
    def test_extract_all_success(self, mock_sleep, mock_extract_data):
        """Test extract_all dengan data di setiap halaman"""
        # Setup mock returns
        mock_extract_data.side_effect = [
            [{'title': 'Product 1', 'price': '$10'}],  # Page 1
            [{'title': 'Product 2', 'price': '$20'}],  # Page 2
            []  # Page 3 (empty)
        ]

        result = extract_all("https://example.com", max_pages=3)

        assert len(result) == 2
        assert result[0]['title'] == "Product 1"
        assert result[1]['title'] == "Product 2"

        # Verify extract_data called 3 times
        assert mock_extract_data.call_count == 3

        # Verify sleep called 2 times (once per page)
        assert mock_sleep.call_count == 2

    @patch('utils.extract.extract_data')
    @patch('time.sleep')
    def test_extract_all_single_page(self, mock_sleep, mock_extract_data):
        """Test extract_all dengan max_pages=1"""
        mock_extract_data.return_value = [{'title': 'Single Product', 'price': '$30'}]

        result = extract_all("https://example.com", max_pages=1)

        assert len(result) == 1
        assert result[0]['title'] == "Single Product"
        assert mock_extract_data.call_count == 1
        assert mock_sleep.call_count == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
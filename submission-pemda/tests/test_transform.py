import pytest
import pandas as pd
import numpy as np

from utils.transform import (
    clean_price,
    clean_rating,
    clean_colors,
    clean_size,
    clean_gender,
    transform_data
)


class TestCleanPrice:
    """Test cases untuk fungsi clean_price"""

    def test_clean_price_usd_conversion(self):
        """Test konversi USD ke IDR"""
        result = clean_price("$50.00")
        assert result == 800000.0  # 50 * 16000

    def test_clean_price_idr_no_conversion(self):
        """Test harga IDR tetap sama"""
        result = clean_price("Rp 100000")
        assert result == 100000.0

    def test_clean_price_none_input(self):
        """Test input None"""
        result = clean_price(None)
        assert result is None

    def test_clean_price_nan_input(self):
        """Test input NaN"""
        result = clean_price(pd.NA)
        assert result is None

    def test_clean_price_no_numbers(self):
        """Test string tanpa angka"""
        result = clean_price("No price")
        assert result is None

    def test_clean_price_mixed_text(self):
        """Test text campuran"""
        result = clean_price("Price: $25.99 USD")
        assert result == 415840.0  # 25.99 * 16000


class TestCleanRating:
    """Test cases untuk fungsi clean_rating"""

    def test_clean_rating_standard(self):
        """Test rating standard"""
        result = clean_rating("Rating: 4.5/5")
        assert result == 4.5

    def test_clean_rating_decimal(self):
        """Test rating dengan desimal"""
        result = clean_rating("4.75")
        assert result == 4.75

    def test_clean_rating_no_decimal(self):
        """Test rating tanpa desimal"""
        result = clean_rating("Rating: 3/5")
        assert result == 3.0

    def test_clean_rating_none_input(self):
        """Test input None"""
        result = clean_rating(None)
        assert result is None

    def test_clean_rating_no_numbers(self):
        """Test string tanpa angka"""
        result = clean_rating("No rating")
        assert result is None


class TestCleanColors:
    """Test cases untuk fungsi clean_colors"""

    def test_clean_colors_standard(self):
        """Test colors standard"""
        result = clean_colors("Colors: 5")
        assert result == 5

    def test_clean_colors_text(self):
        """Test colors dengan text"""
        result = clean_colors("5 colors available")
        assert result == 5

    def test_clean_colors_none_input(self):
        """Test input None"""
        result = clean_colors(None)
        assert result is None

    def test_clean_colors_no_numbers(self):
        """Test string tanpa angka"""
        result = clean_colors("Multiple colors")
        assert result is None


class TestCleanSize:
    """Test cases untuk fungsi clean_size"""

    def test_clean_size_with_prefix(self):
        """Test size dengan prefix"""
        result = clean_size("Size: Large")
        assert result == "Large"

    def test_clean_size_without_prefix(self):
        """Test size tanpa prefix"""
        result = clean_size("Medium")
        assert result == "Medium"

    def test_clean_size_none_input(self):
        """Test input None"""
        result = clean_size(None)
        assert result is None

    def test_clean_size_empty_after_clean(self):
        """Test size yang kosong setelah clean"""
        result = clean_size("Size:")
        assert result is None


class TestCleanGender:
    """Test cases untuk fungsi clean_gender"""

    def test_clean_gender_with_prefix(self):
        """Test gender dengan prefix"""
        result = clean_gender("Gender: Male")
        assert result == "Male"

    def test_clean_gender_without_prefix(self):
        """Test gender tanpa prefix"""
        result = clean_gender("Female")
        assert result == "Female"

    def test_clean_gender_none_input(self):
        """Test input None"""
        result = clean_gender(None)
        assert result is None


class TestTransformData:
    """Test cases untuk fungsi transform_data"""

    def test_transform_data_complete(self):
        """Test transform data lengkap"""
        test_data = [
            {
                "title": "Test Product 1",
                "price": "$29.99",
                "rating": "Rating: 4.5/5",
                "colors": "Colors: 3",
                "size": "Size: Large",
                "gender": "Gender: Unisex"
            },
            {
                "title": "Test Product 2",
                "price": "Rp 150000",
                "rating": "Rating: 3.0/5",
                "colors": "2 colors",
                "size": "Medium",
                "gender": "Male"
            }
        ]

        result = transform_data(test_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

        # Check USD conversion
        assert result.iloc[0]['price'] == 479840.0  # 29.99 * 16000

        # Check IDR no conversion
        assert result.iloc[1]['price'] == 150000.0

        # Check rating cleaning
        assert result.iloc[0]['rating'] == 4.5
        assert result.iloc[1]['rating'] == 3.0

        # Check colors cleaning
        assert result.iloc[0]['colors'] == 3
        assert result.iloc[1]['colors'] == 2

        # Check size cleaning
        assert result.iloc[0]['size'] == "Large"
        assert result.iloc[1]['size'] == "Medium"

        # Check gender cleaning
        assert result.iloc[0]['gender'] == "Unisex"
        assert result.iloc[1]['gender'] == "Male"

    def test_transform_data_missing_columns(self):
        """Test transform data dengan kolom missing"""
        test_data = [
            {"title": "Product 1", "price": "$10.00"}
        ]

        result = transform_data(test_data)

        # Should have all expected columns
        expected_columns = ["title", "price", "rating", "size", "gender", "colors"]
        for col in expected_columns:
            assert col in result.columns

        assert len(result) == 1
        assert result.iloc[0]['price'] == 160000.0  # 10 * 16000"

    def test_transform_data_empty_input(self):
        """Test transform data kosong"""
        result = transform_data([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

        # Should have all expected columns
        expected_columns = ["title", "price", "rating", "size", "gender", "colors"]
        for col in expected_columns:
            assert col in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
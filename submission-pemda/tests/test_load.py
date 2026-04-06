import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, MagicMock

from utils.load import load_to_csv


class TestLoadToCsv:
    """Test cases untuk fungsi load_to_csv"""

    def test_load_to_csv_dataframe_input(self):
        """Test load_to_csv dengan input DataFrame"""
        test_data = pd.DataFrame({
            'title': ['Product 1', 'Product 2'],
            'price': [100000.0, 200000.0],
            'rating': [4.5, 3.0]
        })

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            load_to_csv(test_data, file_path=temp_path)
            assert os.path.exists(temp_path)
            result_df = pd.read_csv(temp_path)
            assert len(result_df) == 2
            assert result_df.iloc[0]['title'] == 'Product 1'
            assert result_df.iloc[0]['price'] == 100000.0
            assert result_df.iloc[1]['title'] == 'Product 2'
            assert result_df.iloc[1]['price'] == 200000.0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_to_csv_list_input(self):
        """Test load_to_csv dengan input list of dict"""
        test_data = [
            {'title': 'Product A', 'price': 50000.0},
            {'title': 'Product B', 'price': 75000.0}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            load_to_csv(test_data, file_path=temp_path)
            assert os.path.exists(temp_path)
            result_df = pd.read_csv(temp_path)
            assert len(result_df) == 2
            assert result_df.iloc[0]['title'] == 'Product A'
            assert result_df.iloc[1]['title'] == 'Product B'
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_to_csv_invalid_input(self):
        """Test load_to_csv dengan input invalid"""
        with pytest.raises(TypeError):
            load_to_csv("invalid input")

    def test_load_to_csv_default_filename(self):
        """Test load_to_csv dengan filename default"""
        test_data = pd.DataFrame({'title': ['Test'], 'price': [1000.0]})
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                load_to_csv(test_data)
                assert os.path.exists('output.csv')
                result_df = pd.read_csv('output.csv')
                assert len(result_df) == 1
                assert result_df.iloc[0]['title'] == 'Test'
            finally:
                os.chdir(original_cwd)

    def test_load_to_csv_creates_directory(self):
        """Test load_to_csv membuat direktori target jika tidak ada"""
        test_data = pd.DataFrame({'title': ['Test'], 'price': [1000.0]})
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'nested', 'output.csv')
            load_to_csv(test_data, file_path=file_path)
            assert os.path.exists(file_path)


class TestLoadToPostgresMock:
    """Mock tests untuk load_to_postgres"""

    @patch('utils.load.create_engine')
    @patch('os.getenv')
    def test_load_to_postgres_success_mock(self, mock_getenv, mock_create_engine):
        """Test load_to_postgres dengan mock"""
        mock_getenv.return_value = None
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        test_data = pd.DataFrame({
            'title': ['Product 1'],
            'price': [100000.0]
        })

        from utils.load import load_to_postgres
        load_to_postgres(test_data, db_url="postgresql://test:test@localhost/test")
        mock_create_engine.assert_called_once_with("postgresql://test:test@localhost/test")

    def test_load_to_postgres_no_url(self):
        """Test load_to_postgres tanpa database URL"""
        from utils.load import load_to_postgres
        test_data = pd.DataFrame({'title': ['Test']})

        with pytest.raises(ValueError, match="DATABASE_URL tidak ditemukan"):
            load_to_postgres(test_data)


class TestLoadToSheetMock:
    """Mock tests for load_to_sheet"""

    @patch('utils.load.build')
    @patch('utils.load.Credentials.from_service_account_file')
    def test_load_to_sheet_success_mock(self, mock_credentials, mock_build):
        mock_creds = MagicMock()
        mock_credentials.return_value = mock_creds
        service_mock = MagicMock()
        update_mock = service_mock.spreadsheets.return_value.values.return_value.update
        update_mock.return_value.execute.return_value = {}
        mock_build.return_value = service_mock

        from utils.load import load_to_sheet
        df = pd.DataFrame({'title': ['Product 1'], 'price': [100000.0]})

        load_to_sheet(df, spreadsheet_id="sheet-id", range_name="Sheet1!A1", credentials_file="creds.json")

        mock_credentials.assert_called_once_with("creds.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
        update_mock.assert_called_once()

    def test_load_to_sheet_missing_spreadsheet_id(self):
        from utils.load import load_to_sheet
        df = pd.DataFrame({'title': ['Product 1'], 'price': [100000.0]})

        with pytest.raises(ValueError, match="Spreadsheet ID harus ditetapkan"):
            load_to_sheet(df, spreadsheet_id="", range_name="Sheet1!A1")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Tests for src.views.export_excel module."""
import pandas as pd
from pathlib import Path

from src.views.export_excel import export_to_excel


class TestExportExcel:

    def test_creates_file(self, tmp_path):
        out = tmp_path / "test_report.xlsx"
        sheets = {"sheet1": pd.DataFrame({"a": [1, 2]})}
        export_to_excel(out, sheets)
        assert out.exists()

    def test_multiple_sheets(self, tmp_path):
        out = tmp_path / "multi.xlsx"
        sheets = {
            "revenue": pd.DataFrame({"rev": [100, 200]}),
            "orders": pd.DataFrame({"cnt": [10, 20]}),
        }
        export_to_excel(out, sheets)
        result = pd.read_excel(out, sheet_name=None)
        assert set(result.keys()) == {"revenue", "orders"}

    def test_long_sheet_name_truncated(self, tmp_path):
        out = tmp_path / "trunc.xlsx"
        long_name = "a" * 50  # Excel limit is 31 chars
        sheets = {long_name: pd.DataFrame({"x": [1]})}
        export_to_excel(out, sheets)
        result = pd.read_excel(out, sheet_name=None)
        assert len(list(result.keys())[0]) <= 31

    def test_creates_parent_directories(self, tmp_path):
        out = tmp_path / "deep" / "nested" / "report.xlsx"
        sheets = {"s": pd.DataFrame({"x": [1]})}
        export_to_excel(out, sheets)
        assert out.exists()

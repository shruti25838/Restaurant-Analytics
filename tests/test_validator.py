"""Tests for src.services.validator module."""
import pytest
import pandas as pd

from src.services.validator import OrderValidator, MenuItemValidator


# ── OrderValidator ───────────────────────────────────────────────────

class TestOrderValidator:

    def test_valid_orders_pass(self):
        df = pd.DataFrame({
            "order_id": [1, 2, 3],
            "order_timestamp": ["2023-01-01 10:00", "2023-01-02 11:00", "2023-01-03 12:00"],
        })
        result = OrderValidator().validate(df)
        assert len(result) == 3

    def test_null_timestamps_dropped(self):
        df = pd.DataFrame({
            "order_id": [1, 2, 3],
            "order_timestamp": ["2023-01-01 10:00", None, "2023-01-03 12:00"],
        })
        result = OrderValidator().validate(df)
        assert len(result) == 2
        assert 2 not in result["order_id"].values

    def test_all_null_timestamps(self):
        df = pd.DataFrame({
            "order_id": [1, 2],
            "order_timestamp": [None, None],
        })
        result = OrderValidator().validate(df)
        assert len(result) == 0

    def test_missing_required_column_raises(self):
        df = pd.DataFrame({"order_id": [1, 2]})
        with pytest.raises(ValueError, match="Missing required columns"):
            OrderValidator().validate(df)

    def test_empty_dataframe(self):
        df = pd.DataFrame({"order_id": [], "order_timestamp": []})
        result = OrderValidator().validate(df)
        assert len(result) == 0

    def test_extra_columns_preserved(self):
        df = pd.DataFrame({
            "order_id": [1],
            "order_timestamp": ["2023-01-01"],
            "location": ["Downtown"],
        })
        result = OrderValidator().validate(df)
        assert "location" in result.columns

    def test_returns_copy_not_view(self):
        df = pd.DataFrame({
            "order_id": [1, 2],
            "order_timestamp": ["2023-01-01", "2023-01-02"],
        })
        result = OrderValidator().validate(df)
        result["order_id"] = 999
        assert df["order_id"].iloc[0] != 999


# ── MenuItemValidator ────────────────────────────────────────────────

class TestMenuItemValidator:

    def test_valid_items_pass(self):
        df = pd.DataFrame({
            "menu_item_id": [1, 2],
            "item_name": ["Burger", "Fries"],
            "unit_price": [60, 40],
        })
        result = MenuItemValidator().validate(df)
        assert len(result) == 2

    def test_null_name_dropped(self):
        df = pd.DataFrame({
            "menu_item_id": [1, 2],
            "item_name": ["Burger", None],
            "unit_price": [60, 40],
        })
        result = MenuItemValidator().validate(df)
        assert len(result) == 1

    def test_null_price_dropped(self):
        df = pd.DataFrame({
            "menu_item_id": [1, 2],
            "item_name": ["Burger", "Fries"],
            "unit_price": [60, None],
        })
        result = MenuItemValidator().validate(df)
        assert len(result) == 1

    def test_missing_column_raises(self):
        df = pd.DataFrame({"menu_item_id": [1]})
        with pytest.raises(ValueError, match="Missing required columns"):
            MenuItemValidator().validate(df)

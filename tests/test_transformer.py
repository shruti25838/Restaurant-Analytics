"""Tests for src.services.transformer module."""
import pandas as pd
import numpy as np

from src.services.transformer import TimestampNormalizer, Deduplicator


# ── TimestampNormalizer ──────────────────────────────────────────────

class TestTimestampNormalizer:

    def test_converts_string_to_datetime(self):
        df = pd.DataFrame({"order_timestamp": ["2023-01-01 10:00:00", "2023-06-15 14:30:00"]})
        result = TimestampNormalizer(["order_timestamp"]).transform(df)
        assert pd.api.types.is_datetime64_any_dtype(result["order_timestamp"])

    def test_invalid_timestamps_become_nat(self):
        df = pd.DataFrame({"order_timestamp": ["2023-01-01", "not-a-date"]})
        result = TimestampNormalizer(["order_timestamp"]).transform(df)
        assert pd.isna(result["order_timestamp"].iloc[1])

    def test_column_not_present_is_skipped(self):
        df = pd.DataFrame({"other_col": [1, 2]})
        result = TimestampNormalizer(["order_timestamp"]).transform(df)
        assert "other_col" in result.columns
        assert "order_timestamp" not in result.columns

    def test_multiple_columns(self):
        df = pd.DataFrame({
            "created_at": ["2023-01-01"],
            "updated_at": ["2023-06-01"],
        })
        result = TimestampNormalizer(["created_at", "updated_at"]).transform(df)
        assert pd.api.types.is_datetime64_any_dtype(result["created_at"])
        assert pd.api.types.is_datetime64_any_dtype(result["updated_at"])

    def test_returns_copy(self):
        df = pd.DataFrame({"order_timestamp": ["2023-01-01"]})
        result = TimestampNormalizer(["order_timestamp"]).transform(df)
        assert result is not df

    def test_empty_dataframe(self):
        df = pd.DataFrame({"order_timestamp": pd.Series([], dtype="object")})
        result = TimestampNormalizer(["order_timestamp"]).transform(df)
        assert len(result) == 0


# ── Deduplicator ─────────────────────────────────────────────────────

class TestDeduplicator:

    def test_removes_duplicates(self):
        df = pd.DataFrame({"id": [1, 1, 2, 3], "value": [10, 10, 20, 30]})
        result = Deduplicator(subset=("id",)).transform(df)
        assert len(result) == 3

    def test_no_duplicates_unchanged(self):
        df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        result = Deduplicator(subset=("id",)).transform(df)
        assert len(result) == 3

    def test_all_duplicates(self):
        df = pd.DataFrame({"id": [1, 1, 1], "value": [10, 10, 10]})
        result = Deduplicator(subset=("id",)).transform(df)
        assert len(result) == 1

    def test_multiple_subset_columns(self):
        df = pd.DataFrame({
            "order_id": [1, 1, 1],
            "item_id": [10, 10, 20],
            "qty": [1, 1, 2],
        })
        result = Deduplicator(subset=("order_id", "item_id")).transform(df)
        assert len(result) == 2

    def test_returns_copy(self):
        df = pd.DataFrame({"id": [1, 2]})
        result = Deduplicator(subset=("id",)).transform(df)
        assert result is not df

    def test_empty_dataframe(self):
        df = pd.DataFrame({"id": []})
        result = Deduplicator(subset=("id",)).transform(df)
        assert len(result) == 0

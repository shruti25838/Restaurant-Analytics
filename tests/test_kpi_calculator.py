"""Tests for src.services.kpi_calculator module."""
import pytest
import pandas as pd
import numpy as np

from src.services.kpi_calculator import (
    DailyRevenueKPI,
    WeeklyRevenueKPI,
    MonthlyRevenueKPI,
    AverageOrderValueKPI,
    OrdersPerDayKPI,
    RevenuePerHourKPI,
    PeakHoursKPI,
    WeekdayVsWeekendKPI,
    TopMenuItemsKPI,
    RevenueByCategoryKPI,
    run_kpi,
)


@pytest.fixture
def sample_detail():
    """Enriched order detail dataframe for KPI tests."""
    return pd.DataFrame({
        "order_id": [1, 1, 2, 2, 3, 3],
        "order_timestamp": pd.to_datetime([
            "2023-01-02 10:00",  # Monday
            "2023-01-02 10:00",
            "2023-01-03 14:00",  # Tuesday
            "2023-01-03 14:00",
            "2023-01-07 19:00",  # Saturday
            "2023-01-07 19:00",
        ]),
        "quantity": [2, 1, 3, 1, 1, 2],
        "item_price": [50.0, 30.0, 50.0, 100.0, 60.0, 40.0],
        "line_total": [100.0, 30.0, 150.0, 100.0, 60.0, 80.0],
        "item_name": ["Burger", "Fries", "Burger", "Pizza", "Latte", "Cookie"],
        "category_name": ["Fastfood", "Fastfood", "Fastfood", "Fastfood", "Coffee", "Desserts"],
    })


# ── DailyRevenueKPI ─────────────────────────────────────────────────

class TestDailyRevenueKPI:

    def test_correct_daily_totals(self, sample_detail):
        result = DailyRevenueKPI().calculate(sample_detail)
        assert len(result) == 3  # 3 distinct days
        assert result["total_revenue"].sum() == 520.0

    def test_missing_columns_raises(self):
        df = pd.DataFrame({"order_id": [1]})
        with pytest.raises(ValueError):
            DailyRevenueKPI().calculate(df)

    def test_name_attribute(self):
        assert DailyRevenueKPI().name == "daily_revenue"


# ── WeeklyRevenueKPI ────────────────────────────────────────────────

class TestWeeklyRevenueKPI:

    def test_aggregates_by_week(self, sample_detail):
        result = WeeklyRevenueKPI().calculate(sample_detail)
        assert "week" in result.columns
        assert "year" in result.columns
        assert result["total_revenue"].sum() == 520.0


# ── MonthlyRevenueKPI ───────────────────────────────────────────────

class TestMonthlyRevenueKPI:

    def test_aggregates_by_month(self, sample_detail):
        result = MonthlyRevenueKPI().calculate(sample_detail)
        assert "year_month" in result.columns
        assert result["total_revenue"].sum() == 520.0


# ── AverageOrderValueKPI ────────────────────────────────────────────

class TestAverageOrderValueKPI:

    def test_correct_aov(self, sample_detail):
        # Order 1: 130, Order 2: 250, Order 3: 140 → mean = 173.33
        result = AverageOrderValueKPI().calculate(sample_detail)
        assert len(result) == 1
        aov = result["average_order_value"].iloc[0]
        assert abs(aov - 173.33) < 1.0

    def test_missing_columns_raises(self):
        df = pd.DataFrame({"order_id": [1]})
        with pytest.raises(ValueError):
            AverageOrderValueKPI().calculate(df)


# ── OrdersPerDayKPI ─────────────────────────────────────────────────

class TestOrdersPerDayKPI:

    def test_correct_counts(self, sample_detail):
        result = OrdersPerDayKPI().calculate(sample_detail)
        assert len(result) == 3
        assert result["orders_count"].sum() == 3


# ── RevenuePerHourKPI ───────────────────────────────────────────────

class TestRevenuePerHourKPI:

    def test_groups_by_hour(self, sample_detail):
        result = RevenuePerHourKPI().calculate(sample_detail)
        assert "hour" in result.columns
        hours = set(result["hour"])
        assert 10 in hours
        assert 14 in hours
        assert 19 in hours


# ── PeakHoursKPI ────────────────────────────────────────────────────

class TestPeakHoursKPI:

    def test_sorted_descending(self, sample_detail):
        result = PeakHoursKPI().calculate(sample_detail)
        counts = result["orders_count"].tolist()
        assert counts == sorted(counts, reverse=True)


# ── WeekdayVsWeekendKPI ─────────────────────────────────────────────

class TestWeekdayVsWeekendKPI:

    def test_weekday_weekend_split(self, sample_detail):
        result = WeekdayVsWeekendKPI().calculate(sample_detail)
        assert set(result["day_type"]) == {"weekday", "weekend"}
        weekday = result.loc[result["day_type"] == "weekday"]
        weekend = result.loc[result["day_type"] == "weekend"]
        assert weekday["orders_count"].iloc[0] == 2
        assert weekend["orders_count"].iloc[0] == 1


# ── TopMenuItemsKPI ──────────────────────────────────────────────────

class TestTopMenuItemsKPI:

    def test_sorted_by_revenue(self, sample_detail):
        result = TopMenuItemsKPI().calculate(sample_detail)
        revenues = result["total_revenue"].tolist()
        assert revenues == sorted(revenues, reverse=True)

    def test_missing_column_raises(self):
        df = pd.DataFrame({"order_id": [1], "quantity": [1], "line_total": [10]})
        with pytest.raises(ValueError):
            TopMenuItemsKPI().calculate(df)


# ── RevenueByCategoryKPI ─────────────────────────────────────────────

class TestRevenueByCategoryKPI:

    def test_groups_by_category(self, sample_detail):
        result = RevenueByCategoryKPI().calculate(sample_detail)
        assert set(result["category_name"]) == {"Fastfood", "Coffee", "Desserts"}
        assert result["total_revenue"].sum() == 520.0

    def test_missing_column_raises(self):
        df = pd.DataFrame({"order_id": [1], "quantity": [1], "line_total": [10]})
        with pytest.raises(ValueError):
            RevenueByCategoryKPI().calculate(df)


# ── run_kpi helper ───────────────────────────────────────────────────

class TestRunKPI:

    def test_delegates_to_calculate(self, sample_detail):
        result = run_kpi(DailyRevenueKPI(), sample_detail)
        assert "total_revenue" in result.columns

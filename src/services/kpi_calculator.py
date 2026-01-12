from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class KPIBase(Protocol):
    name: str

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


# ── Revenue KPIs ─────────────────────────────────────────────────────

@dataclass
class DailyRevenueKPI:
    name: str = "daily_revenue"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not {"order_timestamp", "line_total"}.issubset(df.columns):
            raise ValueError("Expected columns: order_timestamp, line_total")
        return (
            df.assign(order_date=df["order_timestamp"].dt.date)
            .groupby("order_date", as_index=False)["line_total"]
            .sum()
            .rename(columns={"line_total": "total_revenue"})
        )


@dataclass
class WeeklyRevenueKPI:
    name: str = "weekly_revenue"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        tmp = df.copy()
        tmp["week"] = tmp["order_timestamp"].dt.isocalendar().week.astype(int)
        tmp["year"] = tmp["order_timestamp"].dt.year
        return (
            tmp.groupby(["year", "week"], as_index=False)["line_total"]
            .sum()
            .rename(columns={"line_total": "total_revenue"})
        )


@dataclass
class MonthlyRevenueKPI:
    name: str = "monthly_revenue"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        tmp = df.copy()
        tmp["year_month"] = tmp["order_timestamp"].dt.to_period("M").astype(str)
        return (
            tmp.groupby("year_month", as_index=False)["line_total"]
            .sum()
            .rename(columns={"line_total": "total_revenue"})
        )


# ── Order KPIs ───────────────────────────────────────────────────────

@dataclass
class AverageOrderValueKPI:
    name: str = "average_order_value"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not {"order_id", "line_total"}.issubset(df.columns):
            raise ValueError("Expected columns: order_id, line_total")
        order_totals = df.groupby("order_id", as_index=False)["line_total"].sum()
        return pd.DataFrame({"average_order_value": [round(order_totals["line_total"].mean(), 2)]})


@dataclass
class OrdersPerDayKPI:
    name: str = "orders_per_day"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        tmp = df.copy()
        tmp["order_date"] = tmp["order_timestamp"].dt.date
        return (
            tmp.groupby("order_date", as_index=False)["order_id"]
            .nunique()
            .rename(columns={"order_id": "orders_count"})
        )


# ── Time-based KPIs ─────────────────────────────────────────────────

@dataclass
class RevenuePerHourKPI:
    name: str = "revenue_per_hour"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        tmp = df.copy()
        tmp["hour"] = tmp["order_timestamp"].dt.hour
        return (
            tmp.groupby("hour", as_index=False)["line_total"]
            .sum()
            .rename(columns={"line_total": "total_revenue"})
        )


@dataclass
class PeakHoursKPI:
    name: str = "peak_hours"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        tmp = df.copy()
        tmp["hour"] = tmp["order_timestamp"].dt.hour
        hourly = (
            tmp.groupby("hour", as_index=False)["order_id"]
            .nunique()
            .rename(columns={"order_id": "orders_count"})
            .sort_values("orders_count", ascending=False)
        )
        return hourly


@dataclass
class WeekdayVsWeekendKPI:
    name: str = "weekday_vs_weekend"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        tmp = df.copy()
        tmp["day_type"] = tmp["order_timestamp"].dt.dayofweek.apply(
            lambda d: "weekend" if d >= 5 else "weekday"
        )
        return (
            tmp.groupby("day_type", as_index=False)
            .agg(
                orders_count=("order_id", "nunique"),
                total_revenue=("line_total", "sum"),
            )
        )


# ── Menu / Category KPIs ────────────────────────────────────────────

@dataclass
class TopMenuItemsKPI:
    name: str = "top_menu_items"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if "item_name" not in df.columns:
            raise ValueError("Expected column: item_name")
        return (
            df.groupby("item_name", as_index=False)
            .agg(
                total_quantity=("quantity", "sum"),
                total_revenue=("line_total", "sum"),
            )
            .sort_values("total_revenue", ascending=False)
        )


@dataclass
class RevenueByCategoryKPI:
    name: str = "revenue_by_category"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if "category_name" not in df.columns:
            raise ValueError("Expected column: category_name")
        return (
            df.groupby("category_name", as_index=False)
            .agg(
                total_quantity=("quantity", "sum"),
                total_revenue=("line_total", "sum"),
            )
            .sort_values("total_revenue", ascending=False)
        )


# ── Convenience runner ───────────────────────────────────────────────

def run_kpi(kpi: KPIBase, df: pd.DataFrame) -> pd.DataFrame:
    return kpi.calculate(df)

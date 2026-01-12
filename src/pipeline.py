"""Main ETL pipeline.

Reads raw CSVs, validates, transforms, computes all KPIs, exports
results to data/warehouse/ as Excel/CSV, and loads into a SQLite database.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.db_config import get_database_url
from src.services.data_loader import SqlAlchemyRepository
from src.services.transformer import TimestampNormalizer, Deduplicator
from src.services.validator import OrderValidator
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
)
from src.views.export_excel import export_to_excel


def _csv(base: Path, name: str) -> pd.DataFrame | None:
    path = base / name
    if path.exists():
        return pd.read_csv(path)
    return None


def run_pipeline() -> None:
    raw = Path("data/raw")
    warehouse = Path("data/warehouse")
    staging = Path("data/staging")
    warehouse.mkdir(parents=True, exist_ok=True)
    staging.mkdir(parents=True, exist_ok=True)

    # ── 1. Load raw CSVs ─────────────────────────────────────────────
    orders = _csv(raw, "orders.csv")
    order_items = _csv(raw, "order_items.csv")
    menu_items = _csv(raw, "menu_items.csv")
    categories = _csv(raw, "categories.csv")
    customers = _csv(raw, "customers.csv")
    payments = _csv(raw, "payments.csv")
    staff = _csv(raw, "staff.csv")

    if orders is None or order_items is None:
        print("ERROR: orders.csv and order_items.csv are required in data/raw/")
        return

    # ── 2. Validate ──────────────────────────────────────────────────
    orders = OrderValidator().validate(orders)
    order_items = Deduplicator(subset=("order_item_id",)).transform(order_items)

    # ── 3. Transform ─────────────────────────────────────────────────
    orders = TimestampNormalizer(["order_timestamp"]).transform(orders)

    # ── 4. Build enriched detail table ───────────────────────────────
    detail = order_items.merge(
        orders[["order_id", "order_timestamp", "location"]],
        on="order_id",
        how="left",
    )
    detail["line_total"] = detail["quantity"] * detail["item_price"]

    if menu_items is not None:
        detail = detail.merge(
            menu_items[["menu_item_id", "item_name", "category_id"]],
            on="menu_item_id",
            how="left",
        )
    if categories is not None and "category_id" in detail.columns:
        detail = detail.merge(
            categories[["category_id", "category_name"]],
            on="category_id",
            how="left",
        )

    detail.to_csv(staging / "order_detail.csv", index=False)
    print(f"[staging] {len(detail):,} order detail rows")

    # ── 5. Compute KPIs ──────────────────────────────────────────────
    kpis: dict[str, pd.DataFrame] = {}

    kpis["daily_revenue"] = DailyRevenueKPI().calculate(detail)
    kpis["weekly_revenue"] = WeeklyRevenueKPI().calculate(detail)
    kpis["monthly_revenue"] = MonthlyRevenueKPI().calculate(detail)
    kpis["average_order_value"] = AverageOrderValueKPI().calculate(detail)
    kpis["orders_per_day"] = OrdersPerDayKPI().calculate(detail)
    kpis["revenue_per_hour"] = RevenuePerHourKPI().calculate(detail)
    kpis["peak_hours"] = PeakHoursKPI().calculate(detail)
    kpis["weekday_vs_weekend"] = WeekdayVsWeekendKPI().calculate(detail)

    if "item_name" in detail.columns:
        kpis["top_menu_items"] = TopMenuItemsKPI().calculate(detail)
    if "category_name" in detail.columns:
        kpis["revenue_by_category"] = RevenueByCategoryKPI().calculate(detail)

    # ── 6. Export to CSV + Excel ─────────────────────────────────────
    for name, df in kpis.items():
        df.to_csv(warehouse / f"{name}.csv", index=False)
    export_to_excel(warehouse / "kpi_report.xlsx", kpis)

    print(f"[warehouse] {len(kpis)} KPI tables exported")
    for name, df in kpis.items():
        print(f"  {name}: {len(df)} rows")

    # ── 7. Load into database (SQLite by default) ────────────────────
    db_url = get_database_url()
    repo = SqlAlchemyRepository(db_url)

    # Determine which SQL dialect to use
    is_sqlite = "sqlite" in db_url
    schema_dir = Path("sql/schema")
    views_dir = Path("sql/views")

    if is_sqlite:
        schema_file = schema_dir / "create_tables_sqlite.sql"
        view_files = sorted(views_dir.glob("*_sqlite.sql"))
    else:
        schema_file = schema_dir / "create_tables.sql"
        view_files = [f for f in sorted(views_dir.glob("*.sql")) if "_sqlite" not in f.name]

    # Create tables
    if schema_file.exists():
        repo.execute_sql(schema_file.read_text(encoding="utf-8"))
        print(f"[db] Schema applied: {schema_file.name}")

    # Load data into tables (order matters for FK constraints)
    load_order = [
        ("categories", categories),
        ("menu_items", menu_items),
        ("customers", customers),
        ("staff", staff),
        ("orders", orders),
        ("order_items", order_items),
        ("payments", payments),
    ]
    for table_name, df in load_order:
        if df is not None and not df.empty:
            repo.load_dataframe(table_name, df)
            print(f"  [db] {table_name}: {len(df):,} rows loaded")

    # Create views
    for vf in view_files:
        repo.execute_sql(vf.read_text(encoding="utf-8"))
        print(f"  [db] View applied: {vf.name}")

    # Verify views
    print("\n[db] View verification:")
    for view_name in [
        "kpi_daily_revenue", "kpi_average_order_value", "kpi_revenue_by_category",
        "kpi_revenue_per_hour", "kpi_top_menu_items", "kpi_weekday_vs_weekend",
        "sales_trends_hourly", "sales_weekday_vs_weekend",
    ]:
        try:
            result = repo.fetch_dataframe(f"SELECT COUNT(*) AS cnt FROM {view_name}")
            print(f"  {view_name}: {result['cnt'].iloc[0]} rows")
        except Exception:
            pass

    print(f"\n[done] Database: {db_url}")
    print("[done] Excel: data/warehouse/kpi_report.xlsx")
    print("[done] Pipeline complete!")


if __name__ == "__main__":
    run_pipeline()

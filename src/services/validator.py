from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class Validator(Protocol):
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


@dataclass
class OrderValidator:
    required_columns: tuple[str, ...] = ("order_id", "order_timestamp")

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return df.dropna(subset=["order_timestamp"]).copy()


@dataclass
class MenuItemValidator:
    required_columns: tuple[str, ...] = ("menu_item_id", "item_name", "unit_price")

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return df.dropna(subset=["item_name", "unit_price"]).copy()


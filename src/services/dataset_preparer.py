from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def _snake_case(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


@dataclass
class RestaurantDatasetPreparer:
    source_path: Path
    output_dir: Path

    def prepare(self) -> None:
        df = pd.read_csv(self.source_path)
        df.columns = [_snake_case(c) for c in df.columns]

        bool_cols = [
            "has_table_booking",
            "has_online_delivery",
            "is_delivering_now",
            "switch_to_order_menu",
        ]
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].map({"Yes": True, "No": False}).fillna(False)

        cuisines_series = df["cuisines"].fillna("").astype(str)
        cuisines_split = cuisines_series.str.split(",")

        categories = (
            pd.Series([c.strip() for row in cuisines_split for c in row if c.strip()])
            .drop_duplicates()
            .sort_values()
            .reset_index(drop=True)
        )
        categories_df = pd.DataFrame(
            {"category_id": range(1, len(categories) + 1), "category_name": categories}
        )

        category_lookup = dict(zip(categories_df["category_name"], categories_df["category_id"]))
        restaurant_categories = []
        for restaurant_id, cuisine_list in zip(df["restaurant_id"], cuisines_split):
            for cuisine in cuisine_list:
                cuisine = cuisine.strip()
                if cuisine:
                    restaurant_categories.append(
                        {"restaurant_id": restaurant_id, "category_id": category_lookup[cuisine]}
                    )
        restaurant_categories_df = pd.DataFrame(restaurant_categories)

        restaurants_df = df.drop(columns=["cuisines"])

        self.output_dir.mkdir(parents=True, exist_ok=True)
        restaurants_df.to_csv(self.output_dir / "restaurants.csv", index=False)
        categories_df.to_csv(self.output_dir / "categories.csv", index=False)
        restaurant_categories_df.to_csv(
            self.output_dir / "restaurant_categories.csv", index=False
        )


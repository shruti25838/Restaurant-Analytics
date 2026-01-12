from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass
class TimestampNormalizer:
    timestamp_columns: Iterable[str]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        transformed = df.copy()
        for column in self.timestamp_columns:
            if column in transformed.columns:
                transformed[column] = pd.to_datetime(transformed[column], errors="coerce")
        return transformed


@dataclass
class Deduplicator:
    subset: Iterable[str]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates(subset=list(self.subset)).copy()


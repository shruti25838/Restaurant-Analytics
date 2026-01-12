from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterable

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class DataRepository(Protocol):
    def load_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        ...

    def fetch_dataframe(self, query: str) -> pd.DataFrame:
        ...

    def execute_sql(self, statement: str) -> None:
        ...


@dataclass
class SqlAlchemyRepository(DataRepository):
    database_url: str

    def _engine(self) -> Engine:
        return create_engine(self.database_url, future=True)

    def load_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        if df.empty:
            return
        engine = self._engine()
        # SQLite has a variable limit; batch inserts in chunks of 500 rows.
        chunk = 500 if "sqlite" in self.database_url else None
        with engine.begin() as conn:
            df.to_sql(
                table_name, conn, if_exists="append", index=False,
                method="multi", chunksize=chunk,
            )

    def fetch_dataframe(self, query: str) -> pd.DataFrame:
        with self._engine().begin() as conn:
            return pd.read_sql(text(query), conn)

    def execute_sql(self, statement: str) -> None:
        statements = [s.strip() for s in statement.split(";") if s.strip()]
        with self._engine().begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))


def load_csvs(repository: DataRepository, csv_table_map: Iterable[tuple[str, str]]) -> None:
    for csv_path, table_name in csv_table_map:
        df = pd.read_csv(csv_path)
        repository.load_dataframe(table_name, df)


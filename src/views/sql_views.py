from __future__ import annotations

from pathlib import Path
from src.services.data_loader import DataRepository


def apply_sql_file(repository: DataRepository, sql_path: Path) -> None:
    sql_text = sql_path.read_text(encoding="utf-8")
    repository.execute_sql(sql_text)


def apply_all_views(repository: DataRepository) -> None:
    base = Path("sql/views")
    for sql_file in base.glob("*.sql"):
        apply_sql_file(repository, sql_file)


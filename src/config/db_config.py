import os
from pathlib import Path

from dotenv import load_dotenv

# Default to a local SQLite file so the project works out of the box.
_DEFAULT_DB = "sqlite:///" + str(
    Path(__file__).resolve().parents[2] / "data" / "warehouse" / "restaurant.db"
)


def get_database_url() -> str:
    load_dotenv()
    return os.getenv("DATABASE_URL", _DEFAULT_DB)


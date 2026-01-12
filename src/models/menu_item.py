from dataclasses import dataclass
from typing import Optional


@dataclass
class MenuItem:
    menu_item_id: Optional[int]
    category_id: int
    item_name: str
    item_description: Optional[str]
    unit_price: float


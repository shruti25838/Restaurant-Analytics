from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Order:
    order_id: Optional[int]
    customer_id: Optional[int]
    staff_id: Optional[int]
    order_timestamp: datetime
    order_status: str = "completed"
    location: Optional[str] = None


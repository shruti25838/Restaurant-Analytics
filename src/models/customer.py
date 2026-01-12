from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    customer_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: Optional[datetime] = None


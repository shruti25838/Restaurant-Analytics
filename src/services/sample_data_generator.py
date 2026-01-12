"""Generate realistic sample data matching PRD schema.

Inspired by:
- Restaurant Sales Report (Kaggle: rajatsurana979)
- Coffee Shop Sales (Kaggle: dieterholger)

Produces normalized CSVs for all tables in data/raw/.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

# ── Menu categories & items ──────────────────────────────────────────
MENU = {
    "Fastfood": [
        ("Vadapav", 20), ("Aalopuri", 20), ("Samosa", 15), ("Burger", 60),
        ("French Fries", 40), ("Sandwich", 50), ("Pizza Slice", 55),
        ("Spring Roll", 35), ("Wrap", 45), ("Hot Dog", 40),
    ],
    "Beverages": [
        ("Sugarcane Juice", 25), ("Cold Coffee", 50), ("Masala Chai", 15),
        ("Lemonade", 20), ("Mango Lassi", 35), ("Iced Tea", 30),
        ("Fresh Orange Juice", 40), ("Buttermilk", 15),
    ],
    "Coffee": [
        ("Gourmet Brewed Coffee", 45), ("Espresso", 40), ("Latte", 55),
        ("Cappuccino", 50), ("Americano", 40), ("Mocha", 60),
        ("Flat White", 55), ("Cold Brew", 50),
    ],
    "Tea": [
        ("Brewed Chai Tea", 30), ("Green Tea", 25), ("Earl Grey", 30),
        ("Herbal Tea", 28), ("Matcha Latte", 50),
    ],
    "Desserts": [
        ("Chocolate Brownie", 45), ("Gulab Jamun", 30), ("Ice Cream Scoop", 35),
        ("Pastry", 40), ("Cheesecake Slice", 55), ("Cookie", 20),
    ],
    "Main Course": [
        ("Butter Chicken", 180), ("Paneer Tikka", 150), ("Biryani", 160),
        ("Dal Makhani", 120), ("Noodles", 90), ("Fried Rice", 100),
        ("Pasta", 110), ("Grilled Chicken", 170),
    ],
}

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Ayaan", "Krishna", "Ishaan", "Priya", "Ananya", "Diya", "Isha",
    "Saanvi", "Aanya", "Riya", "Meera", "Pooja", "Neha",
    "James", "Emma", "Liam", "Olivia", "Noah", "Ava", "Sophia",
    "Lucas", "Mia", "Ethan",
]
LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Verma", "Reddy",
    "Nair", "Joshi", "Rao", "Smith", "Johnson", "Brown", "Wilson",
    "Taylor", "Anderson", "Thomas", "Garcia", "Martinez", "Davis",
]
STAFF_ROLES = ["Manager", "Cashier", "Chef", "Waiter", "Barista"]
LOCATIONS = ["Downtown", "Mall Court", "Airport Terminal", "Suburb Plaza", "Central Station"]
PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "UPI", "Digital Wallet"]

START_DATE = datetime(2022, 3, 1)
END_DATE = datetime(2023, 3, 31)


def _random_timestamp(date: datetime) -> datetime:
    """Weighted hours: peak at lunch (12-14) and evening (18-21)."""
    hour_weights = (
        [1]*6 + [3]*2 + [5]*2 + [4]*2 + [8]*2 + [6]*2 +
        [4]*2 + [9]*3 + [5]*1
    )
    hours = list(range(6, 23))
    # Trim weights to match hours length
    weights = hour_weights[:len(hours)]
    hour = random.choices(hours, weights=weights, k=1)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return date.replace(hour=hour, minute=minute, second=second)


def generate(output_dir: Path, num_customers: int = 200, num_orders: int = 5000) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Categories ───────────────────────────────────────────────────
    categories = list(MENU.keys())
    categories_df = pd.DataFrame({
        "category_id": range(1, len(categories) + 1),
        "category_name": categories,
    })

    # ── Menu items ───────────────────────────────────────────────────
    menu_rows = []
    menu_id = 1
    for cat_id, (cat_name, items) in enumerate(MENU.items(), start=1):
        for item_name, price in items:
            menu_rows.append({
                "menu_item_id": menu_id,
                "category_id": cat_id,
                "item_name": item_name,
                "item_description": f"{item_name} from our {cat_name} menu",
                "unit_price": price,
            })
            menu_id += 1
    menu_df = pd.DataFrame(menu_rows)

    # ── Customers ────────────────────────────────────────────────────
    customer_rows = []
    for cid in range(1, num_customers + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        customer_rows.append({
            "customer_id": cid,
            "first_name": fn,
            "last_name": ln,
            "email": f"{fn.lower()}.{ln.lower()}{cid}@email.com",
            "phone": f"+91{random.randint(7000000000, 9999999999)}",
            "created_at": (START_DATE + timedelta(days=random.randint(0, 60))).isoformat(),
        })
    customers_df = pd.DataFrame(customer_rows)

    # ── Staff ────────────────────────────────────────────────────────
    staff_rows = []
    for sid in range(1, 11):
        staff_rows.append({
            "staff_id": sid,
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "role": random.choice(STAFF_ROLES),
            "hire_date": (START_DATE - timedelta(days=random.randint(30, 365))).date().isoformat(),
        })
    staff_df = pd.DataFrame(staff_rows)

    # ── Orders + Order Items + Payments ──────────────────────────────
    order_rows = []
    order_item_rows = []
    payment_rows = []
    oi_id = 1
    total_days = (END_DATE - START_DATE).days

    for oid in range(1, num_orders + 1):
        day_offset = random.randint(0, total_days)
        order_date = START_DATE + timedelta(days=day_offset)
        ts = _random_timestamp(order_date)

        cust_id = random.randint(1, num_customers)
        staff_id = random.randint(1, 10)
        location = random.choice(LOCATIONS)

        order_rows.append({
            "order_id": oid,
            "customer_id": cust_id,
            "staff_id": staff_id,
            "order_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": "completed",
            "location": location,
        })

        # 1-5 items per order
        num_items = random.choices([1, 2, 3, 4, 5], weights=[15, 35, 30, 15, 5], k=1)[0]
        chosen_items = random.sample(menu_rows, min(num_items, len(menu_rows)))
        order_total = 0.0

        for item in chosen_items:
            qty = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
            line_price = item["unit_price"]
            order_item_rows.append({
                "order_item_id": oi_id,
                "order_id": oid,
                "menu_item_id": item["menu_item_id"],
                "quantity": qty,
                "item_price": line_price,
            })
            order_total += qty * line_price
            oi_id += 1

        payment_rows.append({
            "payment_id": oid,
            "order_id": oid,
            "payment_method": random.choice(PAYMENT_METHODS),
            "payment_amount": round(order_total, 2),
            "payment_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        })

    orders_df = pd.DataFrame(order_rows)
    order_items_df = pd.DataFrame(order_item_rows)
    payments_df = pd.DataFrame(payment_rows)

    # ── Write all CSVs ───────────────────────────────────────────────
    categories_df.to_csv(output_dir / "categories.csv", index=False)
    menu_df.to_csv(output_dir / "menu_items.csv", index=False)
    customers_df.to_csv(output_dir / "customers.csv", index=False)
    staff_df.to_csv(output_dir / "staff.csv", index=False)
    orders_df.to_csv(output_dir / "orders.csv", index=False)
    order_items_df.to_csv(output_dir / "order_items.csv", index=False)
    payments_df.to_csv(output_dir / "payments.csv", index=False)

    print(f"Generated: {len(categories_df)} categories, {len(menu_df)} menu items, "
          f"{len(customers_df)} customers, {len(staff_df)} staff, "
          f"{len(orders_df)} orders, {len(order_items_df)} order items, "
          f"{len(payments_df)} payments")


if __name__ == "__main__":
    generate(Path("data/raw"))

-- SQLite-compatible schema (used as local default)

CREATE TABLE IF NOT EXISTS customers (
  customer_id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  email TEXT UNIQUE,
  phone TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
  category_id INTEGER PRIMARY KEY,
  category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS menu_items (
  menu_item_id INTEGER PRIMARY KEY,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  item_name TEXT NOT NULL,
  item_description TEXT,
  unit_price REAL NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS staff (
  staff_id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  role TEXT,
  hire_date TEXT
);

CREATE TABLE IF NOT EXISTS orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER REFERENCES customers(customer_id),
  staff_id INTEGER REFERENCES staff(staff_id),
  order_timestamp TEXT NOT NULL,
  order_status TEXT NOT NULL DEFAULT 'completed',
  location TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
  order_item_id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  menu_item_id INTEGER NOT NULL REFERENCES menu_items(menu_item_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  item_price REAL NOT NULL CHECK (item_price >= 0)
);

CREATE TABLE IF NOT EXISTS payments (
  payment_id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  payment_method TEXT NOT NULL,
  payment_amount REAL NOT NULL CHECK (payment_amount >= 0),
  payment_timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory_usage (
  inventory_usage_id INTEGER PRIMARY KEY,
  menu_item_id INTEGER NOT NULL REFERENCES menu_items(menu_item_id),
  usage_date TEXT NOT NULL,
  quantity_used REAL NOT NULL CHECK (quantity_used >= 0),
  unit TEXT
);

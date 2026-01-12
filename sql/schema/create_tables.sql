-- Core entities
CREATE TABLE IF NOT EXISTS customers (
  customer_id SERIAL PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
  category_id SERIAL PRIMARY KEY,
  category_name VARCHAR(100) NOT NULL UNIQUE
);

-- Restaurant directory data (from sample dataset)
CREATE TABLE IF NOT EXISTS restaurants (
  restaurant_id INTEGER PRIMARY KEY,
  restaurant_name VARCHAR(255) NOT NULL,
  country_code INTEGER,
  city VARCHAR(100),
  address TEXT,
  locality VARCHAR(150),
  locality_verbose VARCHAR(200),
  longitude NUMERIC(11, 6),
  latitude NUMERIC(11, 6),
  average_cost_for_two NUMERIC(10, 2),
  currency VARCHAR(50),
  has_table_booking BOOLEAN,
  has_online_delivery BOOLEAN,
  is_delivering_now BOOLEAN,
  switch_to_order_menu BOOLEAN,
  price_range INTEGER,
  aggregate_rating NUMERIC(3, 1),
  rating_color VARCHAR(50),
  rating_text VARCHAR(50),
  votes INTEGER
);

CREATE TABLE IF NOT EXISTS restaurant_categories (
  restaurant_id INTEGER NOT NULL REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  PRIMARY KEY (restaurant_id, category_id)
);

CREATE TABLE IF NOT EXISTS menu_items (
  menu_item_id SERIAL PRIMARY KEY,
  category_id INTEGER NOT NULL REFERENCES categories(category_id),
  item_name VARCHAR(150) NOT NULL,
  item_description TEXT,
  unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS staff (
  staff_id SERIAL PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role VARCHAR(100),
  hire_date DATE
);

CREATE TABLE IF NOT EXISTS orders (
  order_id SERIAL PRIMARY KEY,
  customer_id INTEGER REFERENCES customers(customer_id),
  staff_id INTEGER REFERENCES staff(staff_id),
  order_timestamp TIMESTAMP NOT NULL,
  order_status VARCHAR(50) NOT NULL DEFAULT 'completed',
  location VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS order_items (
  order_item_id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  menu_item_id INTEGER NOT NULL REFERENCES menu_items(menu_item_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  item_price NUMERIC(10, 2) NOT NULL CHECK (item_price >= 0)
);

CREATE TABLE IF NOT EXISTS payments (
  payment_id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
  payment_method VARCHAR(50) NOT NULL,
  payment_amount NUMERIC(10, 2) NOT NULL CHECK (payment_amount >= 0),
  payment_timestamp TIMESTAMP NOT NULL
);

-- Optional inventory usage tracking per menu item
CREATE TABLE IF NOT EXISTS inventory_usage (
  inventory_usage_id SERIAL PRIMARY KEY,
  menu_item_id INTEGER NOT NULL REFERENCES menu_items(menu_item_id),
  usage_date DATE NOT NULL,
  quantity_used NUMERIC(10, 2) NOT NULL CHECK (quantity_used >= 0),
  unit VARCHAR(50)
);


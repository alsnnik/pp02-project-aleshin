import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', dbname='practice_db', user='postgres', password='admin')
cur = conn.cursor()

# Сначала очистим таблицы от старых данных
cur.execute("DROP TABLE IF EXISTS order_items, orders, stock_items, products, categories, sizes, roles, users CASCADE;")

# 1. Создаем таблицы
cur.execute('''
    CREATE TABLE roles (role_id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE);
    CREATE TABLE users (user_id SERIAL PRIMARY KEY, last_name VARCHAR(50), first_name VARCHAR(50), login VARCHAR(50) UNIQUE, password VARCHAR(100), role_id INT REFERENCES roles(role_id));
    CREATE TABLE categories (category_id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE);
    CREATE TABLE sizes (size_id SERIAL PRIMARY KEY, value VARCHAR(20) UNIQUE);
    CREATE TABLE products (product_id SERIAL PRIMARY KEY, name VARCHAR(100), category_id INT REFERENCES categories(category_id), manufacturer VARCHAR(100), price NUMERIC);
    CREATE TABLE stock_items (stock_item_id SERIAL PRIMARY KEY, product_id INT REFERENCES products(product_id), size_id INT REFERENCES sizes(size_id), quantity INT, UNIQUE(product_id, size_id));
    CREATE TABLE orders (order_id SERIAL PRIMARY KEY, user_id INT REFERENCES users(user_id), order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE order_items (order_item_id SERIAL PRIMARY KEY, order_id INT REFERENCES orders(order_id), product_id INT REFERENCES products(product_id), quantity INT);
''')

# 2. Заполняем данными
cur.execute("INSERT INTO roles (name) VALUES ('Администратор'), ('Менеджер'), ('Клиент')")
cur.execute("INSERT INTO users (last_name, first_name, login, password, role_id) VALUES ('Иванов', 'Иван', 'admin', '1234', 1), ('Петров', 'Петр', 'manager1', '1234', 2), ('Сидоров', 'Сидор', 'client1', '1234', 3)")
cur.execute("INSERT INTO categories (name) VALUES ('Диваны'), ('Столы')")
cur.execute("INSERT INTO sizes (value) VALUES ('Стандарт')")
cur.execute("INSERT INTO products (name, category_id, manufacturer, price) VALUES ('Диван Комфорт', 1, 'IKEA', 25000), ('Стол Дуб', 2, 'Bosch', 15000)")
cur.execute("INSERT INTO stock_items (product_id, size_id, quantity) VALUES (1, 1, 10), (2, 1, 5)")
cur.execute("INSERT INTO orders (user_id) VALUES (3)")
cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 1)")

conn.commit()
print("Таблицы созданы, данные добавлены!")
cur.close()
conn.close()
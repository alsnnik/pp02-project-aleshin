import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 5,
                host='localhost',
                port='5432',
                dbname='practice_db',
                user='postgres',
                password='admin',
                client_encoding='UTF8'
            )
        except Exception as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        return self.connection_pool.getconn() if self.connection_pool else None

    def release_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()

    def get_categories(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT name FROM categories")
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка категорий: {e}")
            return []
        finally:
            self.release_connection(conn)

    def get_products(self, search="", category="Все категории", order="ASC"):
        conn = self.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            pattern = f"%{search}%"
            query = f"""
                SELECT p.product_id, p.name, c.name AS category, 
                       p.manufacturer, p.price,
                       COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                WHERE p.name LIKE %s
                  AND (c.name = %s OR %s = 'Все категории')
                GROUP BY p.product_id, c.name, p.manufacturer, p.name, p.price
                ORDER BY p.price {order}
            """
            cur.execute(query, (pattern, category, category))
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка товаров: {e}")
            return []
        finally:
            self.release_connection(conn)

    def get_orders(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            query = """
                SELECT o.order_id, o.order_date, 
                       CONCAT(u.last_name, ' ', u.first_name) AS client_name,
                       COALESCE(SUM(oi.quantity * p.price), 0) AS total_sum
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                LEFT JOIN products p ON oi.product_id = p.product_id
                GROUP BY o.order_id, o.order_date, u.last_name, u.first_name
                ORDER BY o.order_date DESC
            """
            cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка заказов: {e}")
            return []
        finally:
            self.release_connection(conn)

    def get_users(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            query = """
                SELECT u.user_id, u.last_name, u.first_name, u.login, r.name AS role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.role_id
            """
            cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка пользователей: {e}")
            return []
        finally:
            self.release_connection(conn)
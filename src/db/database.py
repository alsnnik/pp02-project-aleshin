import psycopg
from psycopg_pool import ConnectionPool

class Database:
    def __init__(self):
        try:
            # Создаем пул соединений psycopg3
            self.connection_pool = ConnectionPool(
                conninfo="host=localhost port=5432 dbname=interior_db user=postgres password=admin",
                min_size=1,
                max_size=5,
                open=True
            )
            print("Пул соединений PostgreSQL (psycopg3) успешно создан!")
        except Exception as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None
    def get_connection(self):
        # Возвращаем соединение из пула
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    def release_connection(self, conn):
        if self.connection_pool and conn:
            # Возвращаем соединение обратно в пул
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.close()

    def get_categories(self):
        if not self.connection_pool:
            return []
        # ИСПОЛЬЗУЕМ with ДЛЯ ПОЛУЧЕНИЯ СОЕДИНЕНИЯ ИЗ ПУЛА
        with self.connection_pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT DISTINCT name FROM categories")
                    return cur.fetchall()
            except Exception as e:
                print(f"Ошибка категорий: {e}")
                return []

    def get_products(self, search="", category="Все категории", order="ASC"):
        if not self.connection_pool:
            return []
        with self.connection_pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    pattern = f"%{search}%"
                    query = f"""
                        SELECT p.product_id, p.name, c.name AS category, 
                               p.manufacturer, p.price,
                               COALESCE(SUM(si.quantity), 0) AS total_quantity
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.category_id
                        LEFT JOIN stock_items si ON p.product_id = si.product_id
                        WHERE p.name ILIKE %s
                          AND (c.name = %s OR %s = 'Все категории')
                        GROUP BY p.product_id, c.name, p.manufacturer, p.name, p.price
                        ORDER BY p.price {order}
                    """
                    cur.execute(query, (pattern, category, category))
                    return cur.fetchall()
            except Exception as e:
                print(f"Ошибка товаров: {e}")
                return []

    def get_orders(self):
        if not self.connection_pool:
            return []
        with self.connection_pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    query = """
                        SELECT o.order_id, o.order_date, 
                               CONCAT(u.last_name, ' ', u.first_name) AS client_name,
                               COALESCE(SUM(oi.quantity * oi.price), 0) AS total_sum
                        FROM orders o
                        LEFT JOIN users u ON o.user_id = u.user_id
                        LEFT JOIN order_items oi ON o.order_id = oi.order_id
                        GROUP BY o.order_id, o.order_date, u.last_name, u.first_name
                        ORDER BY o.order_date DESC
                    """
                    cur.execute(query)
                    return cur.fetchall()
            except Exception as e:
                print(f"Ошибка заказов: {e}")
                return []

    def get_users(self):
        if not self.connection_pool:
            return []
        with self.connection_pool.connection() as conn:
            try:
                with conn.cursor() as cur:
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

    # Если в login_window.py вызывается метод проверки логина, добавьте его сюда
    def check_user(self, login):
        if not self.connection_pool:
            return None
        with self.connection_pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT u.user_id, u.last_name, u.first_name, u.role_id 
                        FROM users u WHERE u.login = %s
                    """, (login,))
                    return cur.fetchone()
            except Exception as e:
                print(f"Ошибка проверки пользователя: {e}")
                return None
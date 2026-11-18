import psycopg2
import mysql.connector

# Настройки MySQL
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234', # Твой пароль от MySQL
    'database': 'interior_db'
}

# Настройки PostgreSQL
pg_config = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'practice_db',
    'user': 'postgres',
    'password': 'admin'
}

def migrate_data():
    try:
        print("Подключение к MySQL...")
        my_conn = mysql.connector.connect(**mysql_config)
        my_cur = my_conn.cursor()

        print("Подключение к PostgreSQL...")
        pg_conn = psycopg2.connect(**pg_config)
        pg_cur = pg_conn.cursor()

        # Список таблиц, которые нужно перенести (порядок важен из-за связей)
        tables = [
            'roles', 'users', 'categories', 'sizes', 
            'products', 'stock_items', 'orders', 'order_items'
        ]

        # Очищаем таблицы в PostgreSQL перед заливкой (кроме ролей и юзеров, если не хотим)
        pg_cur.execute("TRUNCATE TABLE order_items, orders, stock_items, products, categories, sizes, users, roles RESTART IDENTITY CASCADE")
        
        for table in tables:
            print(f"Перенос таблицы {table}...")
            
            # Получаем данные из MySQL
            my_cur.execute(f"SELECT * FROM {table}")
            rows = my_cur.fetchall()
            
            if not rows:
                print(f"  Таблица {table} пуста.")
                continue

            # Получаем названия колонок
            my_cur.execute(f"SHOW COLUMNS FROM {table}")
            columns = [col[0] for col in my_cur.fetchall()]
            
            # Формируем запрос для вставки
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            try:
                pg_cur.executemany(insert_query, rows)
                pg_conn.commit()
                print(f"  Успешно перенесено {len(rows)} строк.")
            except Exception as e:
                pg_conn.rollback()
                print(f"  Ошибка при вставке в {table}: {e}")

        # Сбрасываем последовательности (чтобы новые ID не конфликтовали)
        for table in tables:
            try:
                pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) FROM {table}")
            except:
                pass # Пропускаем, если колонка называется иначе (например, user_id)
        pg_conn.commit()
        
        print("🎉 Все данные успешно перенесены!")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        if 'my_cur' in locals(): my_cur.close()
        if 'my_conn' in locals(): my_conn.close()
        if 'pg_cur' in locals(): pg_cur.close()
        if 'pg_conn' in locals(): pg_conn.close()

if __name__ == "__main__":
    migrate_data()
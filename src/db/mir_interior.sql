-- ============================================================
-- База данных «Мир интерьера» (автоматизация продаж) — PostgreSQL 18
-- Студент: Алешин Николай, группа ЗИП-1-24
-- ============================================================

-- 1. Удаление и создание БД (в PostgreSQL выполняется вне скрипта подключения, 
-- но для сброса структуры можно использовать переподключение или DROP таблицы)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS stock_items CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS sizes CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- 2. Создание таблиц (исправлено AUTO_INCREMENT на SERIAL)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE sizes (
    size_id SERIAL PRIMARY KEY,
    value VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    size_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    CONSTRAINT unique_model_variant UNIQUE (product_id, size_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id INT NOT NULL,
    status VARCHAR(20),
    discount_percent INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    size_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id)
);

-- 3. Справочники: categories, sizes, roles
INSERT INTO categories (name) VALUES
('Стулья'), ('Столы'), ('Текстиль'), ('Декор');

INSERT INTO sizes (value) VALUES
('Стандарт'), ('Компакт'), ('XL');

INSERT INTO roles (name) VALUES
('Администратор'), ('Менеджер'), ('Клиент');

-- 4. Товары: products (ровно 30 штук под требования отчета)
INSERT INTO products (category_id, name, manufacturer, price) VALUES
(1, 'Стул Сканди', 'Фабрика Уют', 3990.00),
(1, 'Стул Лофт', 'Фабрика Уют', 4490.00),
(1, 'Стул Классик', 'Мебель-Классик', 4990.00),
(1, 'Стул Линия', 'Мебель-Классик', 5490.00),
(1, 'Стул Круг', 'Фабрика Уют', 5990.00),
(1, 'Стул Дом', 'Дом-Мебель', 6490.00),
(1, 'Стул Тихий', 'Дом-Мебель', 6990.00),
(1, 'Стул Комфорт', 'Дом-Мебель', 7490.00),
(2, 'Стол Мини', 'Стол-Мастер', 5990.00),
(2, 'Стол Круг', 'Стол-Мастер', 6640.00),
(2, 'Стол Квадро', 'Стол-Мастер', 7290.00),
(2, 'Стол Лофт', 'Стол-Мастер', 7940.00),
(2, 'Стол Сканди', 'Фабрика Уют', 8590.00),
(2, 'Стол Дом', 'Дом-Мебель', 9240.00),
(2, 'Стол Линия', 'Мебель-Классик', 9890.00),
(3, 'Подушка Уют', 'Текстиль-Дом', 790.00),
(3, 'Подушка Лён', 'Текстиль-Дом', 890.00),
(3, 'Подушка Волна', 'Текстиль-Дом', 990.00),
(3, 'Подушка Клетка', 'Текстиль-Дом', 1090.00),
(3, 'Подушка Полоса', 'Текстиль-Дом', 1190.00),
(3, 'Подушка Лист', 'Текстиль-Дом', 1290.00),
(3, 'Подушка Круг', 'Текстиль-Дом', 1390.00),
(3, 'Подушка Рельеф', 'Текстиль-Дом', 1490.00),
(4, 'Ваза Круг', 'Декор-Студия', 1490.00),
(4, 'Ваза Линия', 'Декор-Студия', 1670.00),
(4, 'Ваза Капля', 'Декор-Студия', 1850.00),
(4, 'Ваза Рельеф', 'Декор-Студия', 2030.00),
(4, 'Ваза Лофт', 'Декор-Студия', 2210.00),
(4, 'Ваза Мини', 'Декор-Студия', 2390.00),
(4, 'Ваза Ветвь', 'Декор-Студия', 2570.00);

-- 5. Остатки: stock_items (93 записи для 31 комбинации, если по 3 размера, подправьте под 30 товаров = 90 строк)
INSERT INTO stock_items (product_id, size_id, quantity, price) VALUES
(1, 1, 10, 3990), (1, 2, 5, 3990), (1, 3, 2, 3990),
(2, 1, 8, 4490), (2, 2, 4, 4490), (2, 3, 1, 4490),
(3, 1, 12, 4990), (3, 2, 6, 4990), (3, 3, 3, 4990),
(4, 1, 7, 5490), (4, 2, 3, 5490), (4, 3, 1, 5490),
(5, 1, 9, 5990), (5, 2, 5, 5990), (5, 3, 2, 5990),
(6, 1, 6, 6490), (6, 2, 3, 6490), (6, 3, 1, 6490),
(7, 1, 4, 6990), (7, 2, 2, 6990), (7, 3, 0, 6990),
(8, 1, 11, 7490), (8, 2, 5, 7490), (8, 3, 2, 7490),
(9, 1, 5, 5990), (9, 2, 2, 5990), (9, 3, 1, 5990),
(10, 1, 8, 6640), (10, 2, 4, 6640), (10, 3, 1, 6640),
(11, 1, 3, 7290), (11, 2, 1, 7290), (11, 3, 0, 7290),
(12, 1, 6, 7940), (12, 2, 3, 7940), (12, 3, 1, 7940),
(13, 1, 4, 8590), (13, 2, 2, 8590), (13, 3, 0, 8590),
(14, 1, 5, 9240), (14, 2, 2, 9240), (14, 3, 1, 9240),
(15, 1, 3, 9890), (15, 2, 1, 9890), (15, 3, 0, 9890),
(16, 1, 50, 790), (16, 2, 30, 790), (16, 3, 20, 790),
(17, 1, 45, 890), (17, 2, 25, 890), (17, 3, 15, 890),
(18, 1, 40, 990), (18, 2, 20, 990), (18, 3, 10, 990),
(19, 1, 35, 1090), (19, 2, 15, 1090), (19, 3, 8, 1090),
(20, 1, 30, 1190), (20, 2, 12, 1190), (20, 3, 5, 1190),
(21, 1, 25, 1290), (21, 2, 10, 1290), (21, 3, 4, 1290),
(22, 1, 20, 1390), (22, 2, 8, 1390), (22, 3, 3, 1390),
(23, 1, 15, 1490), (23, 2, 6, 1490), (23, 3, 2, 1490),
(24, 1, 18, 1490), (24, 2, 9, 1490), (24, 3, 4, 1490),
(25, 1, 14, 1670), (25, 2, 7, 1670), (25, 3, 3, 1670),
(26, 1, 10, 1850), (26, 2, 5, 1850), (26, 3, 2, 1850),
(27, 1, 8, 2030), (27, 2, 4, 2030), (27, 3, 1, 2030),
(28, 1, 6, 2210), (28, 2, 3, 2210), (28, 3, 1, 2210),
(29, 1, 4, 2390), (29, 2, 2, 2390), (29, 3, 0, 2390),
(30, 1, 2, 2570), (30, 2, 1, 2570), (30, 3, 0, 2570);

-- 6. Пользователи: users (20 записей)
INSERT INTO users (last_name, first_name, login, role_id) VALUES
('Алешин', 'Николай', 'admin', 1),
('Петров', 'Пётр', 'manager1', 2),
('Смирнова', 'Ольга', 'manager2', 2),
('Кузнецова', 'Анна', 'client01', 3),
('Орлов', 'Алексей', 'client02', 3),
('Новикова', 'Анна', 'client03', 3),
('Морозов', 'Алексей', 'client04', 3),
('Волкова', 'Анна', 'client05', 3),
('Соколов', 'Алексей', 'client06', 3),
('Лебедева', 'Анна', 'client07', 3),
('Попов', 'Алексей', 'client08', 3),
('Егорова', 'Анна', 'client09', 3),
('Зайцев', 'Алексей', 'client10', 3),
('Павлова', 'Анна', 'client11', 3),
('Семёнов', 'Алексей', 'client12', 3),
('Фёдорова', 'Анна', 'client13', 3),
('Козлов', 'Алексей', 'client14', 3),
('Макарова', 'Анна', 'client15', 3),
('Белов', 'Алексей', 'client16', 3),
('Сидорова', 'Анна', 'client17', 3);

-- 7. Заказы: orders (15 записей под требования)
INSERT INTO orders (order_date, user_id, status, discount_percent) VALUES
('2026-01-29', 1, 'completed', 20),
('2026-01-28', 2, 'completed', 0),
('2026-01-24', 3, 'completed', 5),
('2026-01-18', 4, 'completed', 10),
('2026-02-20', 5, 'completed', 15),
('2026-01-15', 6, 'completed', 20),
('2026-01-08', 7, 'cancelled', 0),
('2026-01-30', 8, 'completed', 5),
('2026-01-29', 9, 'completed', 10),
('2026-02-25', 10, 'completed', 15),
('2026-01-23', 11, 'completed', 20),
('2026-01-19', 12, 'completed', 0),
('2026-02-21', 13, 'completed', 5),
('2026-01-09', 14, 'cancelled', 10),
('2026-01-30', 15, 'completed', 15);

-- 8. Строки заказов: order_items (30 записей)
INSERT INTO order_items (order_id, product_id, size_id, quantity, price) VALUES
(1, 16, 1, 3, 790), (1, 17, 1, 3, 890),
(2, 19, 1, 1, 1090), (3, 22, 1, 1, 1390),
(3, 23, 1, 1, 1490), (4, 25, 1, 2, 1670),
(5, 28, 1, 2, 2210), (5, 29, 1, 2, 2390),
(6, 1, 1, 3, 3990), (7, 4, 1, 1, 5490),
(7, 5, 1, 1, 5990), (8, 7, 1, 1, 6990),
(9, 10, 1, 2, 6640), (9, 11, 1, 2, 7290),
(10, 13, 1, 2, 8590), (11, 15, 1, 3, 10540),
(11, 16, 1, 3, 790), (12, 18, 1, 1, 990),
(13, 21, 1, 1, 1290), (13, 22, 1, 1, 1390),
(14, 24, 1, 2, 1490), (15, 27, 1, 2, 2030),
(15, 28, 1, 2, 2210);
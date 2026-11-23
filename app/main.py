import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db.database import Database
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                               QPushButton, QMessageBox, QLineEdit, QComboBox,
                               QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                               QStackedWidget)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from login_window import LoginWindow

DISCOUNT_RATE = 0.75

def get_resource_path(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(current_dir, "resources", filename),
        os.path.join(os.path.dirname(current_dir), "resources", filename),
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), "resources", filename)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return possible_paths[0]

def calculate_price_interior(item_id, base_price):
    try:
        temp_db = Database()
        conn = temp_db.get_connection()
        if conn is None:
            return base_price
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s 
            AND o.order_date >= date_trunc('month', CURRENT_DATE - INTERVAL '1 month')
            AND o.order_date < date_trunc('month', CURRENT_DATE)
        """
        cursor.execute(query, (item_id,))
        orders_count = cursor.fetchone()[0]
        cursor.close()
        temp_db.release_connection(conn)
        return round(base_price * DISCOUNT_RATE, 2) if orders_count == 0 else base_price
    except Exception as e:
        print(f"Ошибка БД (расчет скидки): {e}")
        return base_price

class ClickableCard(QWidget):
    def __init__(self, product_data, click_callback):
        super().__init__()
        self.product_data = product_data
        self.click_callback = click_callback
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_callback(self.product_data)

def create_card(product, index, main_window):
    (product_id, name, category, manufacturer, price, total_quantity) = product
    if not manufacturer:
        manufacturer = "Без бренда"

    card = ClickableCard(product, main_window.show_product_info)
    card.setFixedHeight(110)

    card_layout = QHBoxLayout()
    card_layout.setContentsMargins(10, 10, 15, 10)
    card_layout.setSpacing(15)

    # 1. КАРТИНКА
    image_label = QLabel()
    img_name = f"IMG_13_{product_id:03d}.png"
    img_path = get_resource_path(img_name)
    fallback_path = get_resource_path("picture.png")

    if os.path.exists(img_path):
        pixmap = QPixmap(img_path)
    else:
        pixmap = QPixmap(fallback_path)

    image_label.setPixmap(pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(90, 90)
    image_label.setStyleSheet("background-color: transparent;")
    card_layout.addWidget(image_label, alignment=Qt.AlignVCenter)

    # 2. ТЕКСТ
    text_layout = QVBoxLayout()
    text_layout.setSpacing(5)
    text_layout.setAlignment(Qt.AlignVCenter)

    name_label = QLabel(f"{manufacturer} | {name}")
    name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0B2C6F; background-color: transparent;")
    cat_label = QLabel(f"ID Категории: {category}")
    cat_label.setStyleSheet("color: #333333; font-size: 12px; background-color: transparent;")
    qty_label = QLabel(f"Доступно для покупки: {int(total_quantity)} шт.")
    qty_label.setStyleSheet("color: #333333; font-size: 12px; background-color: transparent;")

    text_layout.addWidget(name_label)
    text_layout.addWidget(cat_label)
    text_layout.addWidget(qty_label)
    card_layout.addLayout(text_layout, stretch=1)

    # 3. ЦЕНЫ
    old_price = float(price)
    new_price = calculate_price_interior(product_id, old_price)
    discount_percent = (old_price - new_price) / old_price * 100 if old_price > 0 else 0

    price_layout = QVBoxLayout()
    price_layout.setSpacing(2)
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 12px; background-color: transparent;")
    price_layout.addWidget(old_price_label, alignment=Qt.AlignRight)

    new_price_label = QLabel(f"{new_price:.2f} ₽")
    if discount_percent > 0:
        new_price_label.setStyleSheet("color: #005A2F; font-weight: bold; font-size: 16px; background-color: transparent;")
    else:
        new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 16px; background-color: transparent;")
    price_layout.addWidget(new_price_label, alignment=Qt.AlignRight)

    old_price_label.setVisible(discount_percent > 0)
    card_layout.addLayout(price_layout)
    card.setLayout(card_layout)

    if total_quantity <= 3:
        card.setStyleSheet("background-color: #ff8080; border: none; border-radius: 5px;")
    else:
        card.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 5px;")

    return card


class MainWindow(QMainWindow):
    def __init__(self, user_id=None, role_id=None, full_name=None):
        super().__init__()
        self.user_id = user_id
        self.role_id = role_id
        self.full_name = full_name
        self.db = Database()
        
        role_names = {1: "Администратор", 2: "Менеджер", 3: "Клиент", None: "Гость"}
        self.role_title = role_names.get(self.role_id, "Гость")

        self.setWindowTitle("Мир интерьера — Каталог")
        self.resize(850, 750)
        
        icon_path = get_resource_path("Мир интерьера.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: Calibri; }
            QPushButton {
                background-color: #70B2AF; color: #FFFFFF; 
                font-family: Calibri; font-weight: bold; 
                border-radius: 5px; padding: 5px 15px;
            }
            QPushButton:hover { background-color: #5c9694; }
            QLineEdit, QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 5px;
                background-color: #FFFFFF;
                color: #000000;
                font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #000000;
                selection-background-color: #70B2AF;
                selection-color: #FFFFFF;
            }
        """)

        self.setup_ui()
        self.setup_role_interface()

    # ================== НАВИГАЦИЯ ==================
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        titles = {
            0: "Мир интерьера — Каталог",
            1: "Мир интерьера — Карточка товара",
            2: "Мир интерьера — Заказы",
        }
        self.setWindowTitle(titles[index])
        
        if index == 0:
            self.refresh_catalog()
        elif index == 2:
            self.load_orders()

    def refresh_catalog(self):
        if hasattr(self, "load_products"):
            self.load_products()

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(current_index - 1)

    # ================== UI ==================
    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ШАПКА
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_container = QWidget()
        logo_container.setStyleSheet("background-color: #D2F6E7; border-radius: 5px;")
        logo_layout = QHBoxLayout(logo_container)
        
        logo = QLabel()
        logo_path = get_resource_path("Мир интерьера.png")
        if os.path.exists(logo_path):
            logo.setPixmap(QPixmap(logo_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_layout.addWidget(logo)
        
        logo_text = QLabel("Мир интерьера")
        logo_text.setStyleSheet("font-weight: bold; color: #1a5e3a; font-size: 14px;")
        logo_layout.addWidget(logo_text)
        header_layout.addWidget(logo_container)
        
        header_layout.addStretch()

        text = f"ФИО: {self.full_name} ({self.role_title})" if self.full_name else "ФИО: Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("""
            QPushButton { background-color: #D2F6E7; color: #000000; font-weight: bold; border-radius: 3px; padding: 5px 15px; }
            QPushButton:hover { background-color: #b5e5d3; }
        """)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(header_widget)
        
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #E0E0E0;")
        main_layout.addWidget(line)

        # ВЕРХНИЕ КНОПКИ
        buttons_layout = QHBoxLayout()
        
        self.order_button = QPushButton("Купить товар")
        self.order_button.clicked.connect(self.buy_product)
        buttons_layout.addWidget(self.order_button)

        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.clicked.connect(lambda: self.switch_page(2))
        buttons_layout.addWidget(self.manager_button)

        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.clicked.connect(self.show_admin_panel) 
        buttons_layout.addWidget(self.admin_button)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # СТЕК СТРАНИЦ
        self.stacked_widget = QStackedWidget()

        self.catalog_page = self._create_catalog_page()
        self.product_page = self._create_product_page()
        self.orders_page = self._create_orders_page()

        self.stacked_widget.addWidget(self.catalog_page)   # 0
        self.stacked_widget.addWidget(self.product_page)   # 1
        self.stacked_widget.addWidget(self.orders_page)    # 2
        self.stacked_widget.setCurrentIndex(0)

        main_layout.addWidget(self.stacked_widget)

        # НИЖНИЕ КНОПКИ
        bottom_nav_layout = QHBoxLayout()
        bottom_nav_layout.setContentsMargins(0, 10, 0, 0)
        
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        bottom_nav_layout.addWidget(self.back_button)

        self.btn_page2 = QPushButton("Стр. 2 (Карточка)")
        self.btn_page2.clicked.connect(lambda: self.switch_page(1))
        bottom_nav_layout.addWidget(self.btn_page2)

        self.btn_page3 = QPushButton("Стр. 3 (Заказы)")
        self.btn_page3.clicked.connect(lambda: self.switch_page(2))
        bottom_nav_layout.addWidget(self.btn_page3)

        bottom_nav_layout.addStretch()
        main_layout.addLayout(bottom_nav_layout)

        self.setCentralWidget(central)
        self.load_products()

    def _create_catalog_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        filters_layout = QHBoxLayout()
        filters_layout.setContentsMargins(0, 10, 0, 10)
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию...")
        self.search_input.textChanged.connect(self.load_products)
        
        # ФИЛЬТР КАТЕГОРИЙ
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        
        try:
            categories = self.db.get_categories()
            if categories:
                for cat in categories:
                    cat_name = cat[0] if isinstance(cat, (tuple, list)) else cat
                    if cat_name:
                        self.filter_combo.addItem(str(cat_name))
            else:
                self.filter_combo.addItems(["Столы", "Стулья", "Диваны", "Текстиль", "Освещение"])
        except Exception as e:
            print(f"Ошибка загрузки категорий: {e}")
            self.filter_combo.addItems(["Столы", "Стулья", "Диваны", "Текстиль", "Освещение"])

        self.filter_combo.currentIndexChanged.connect(self.load_products)
        
        # СОРТИРОВКА (Добавлено "цены" в текст)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию цены", "По убыванию цены"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        
        self.filter_combo.setMinimumWidth(150)
        self.sort_combo.setMinimumWidth(180) # Чуть шире, чтобы текст влез
        
        filters_layout.addWidget(self.search_input, 1)
        filters_layout.addWidget(self.filter_combo)
        filters_layout.addWidget(self.sort_combo)
        layout.addLayout(filters_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFFFFF;")
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(10)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        return page

    def _create_product_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Карточка товара")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0B2C6F; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.product_info_label = QLabel("Выберите товар в каталоге.")
        self.product_info_label.setWordWrap(True)
        self.product_info_label.setStyleSheet("font-size: 15px; color: #000000; line-height: 1.5;")
        layout.addWidget(self.product_info_label)
        
        layout.addStretch()
        return page

    def _create_orders_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Заказы")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0B2C6F; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["ID заказа", "Дата", "Клиент", "Сумма (₽)"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.orders_table)
        return page

    # ================== ДАННЫЕ ==================
    def load_products(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        search_text = self.search_input.text().strip()
        category_text = self.filter_combo.currentText()
        
        # ИЗМЕНЕНО: проверяем текст с учетом нового названия
        sort_order = "ASC" if "возрастанию" in self.sort_combo.currentText() else "DESC"

        try:
            products = self.db.get_products(search_text, category_text, sort_order)
            if products:
                for index, product in enumerate(products):
                    self.list_layout.addWidget(create_card(product, index, self))
            else:
                error_label = QLabel("Товары не найдены")
                error_label.setAlignment(Qt.AlignCenter)
                self.list_layout.addWidget(error_label)
        except Exception as e:
            error_label = QLabel(f"ОШИБКА SQL:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            self.list_layout.addWidget(error_label)
            
        self.list_layout.addStretch()

    def show_product_info(self, product_data):
        (p_id, name, category, manufacturer, price, total_quantity) = product_data
        new_price = calculate_price_interior(p_id, float(price))

        self.product_info_label.setText(
            f"<b>Товар:</b> {name}<br>"
            f"<b>Производитель:</b> {manufacturer or 'Без бренда'}<br>"
            f"<b>Категория:</b> {category}<br>"
            f"<b>В наличии:</b> {int(total_quantity)} шт.<br><br>"
            f"<b style='color:#005A2F; font-size:18px;'>Цена: {new_price:.2f} ₽</b>"
        )
        self.switch_page(1)

    def load_orders(self):
        try:
            orders = self.db.get_orders()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить заказы:\n{e}")
            return

        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            o_id, o_date, client, total = order
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(o_id)))
            self.orders_table.setItem(row, 1, QTableWidgetItem(str(o_date)))
            self.orders_table.setItem(row, 2, QTableWidgetItem(str(client)))
            self.orders_table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}"))

    def buy_product(self):
        QMessageBox.information(
            self, "Оформление заказа", 
            "Товар успешно добавлен в корзину! Спасибо за покупку в магазине «Мир интерьера»."
        )

    def show_admin_panel(self):
        users = self.db.get_users()
        dialog = QDialog(self)
        dialog.setWindowTitle("Админ-панель: Пользователи")
        dialog.resize(500, 400)
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Фамилия", "Имя", "Логин", "Роль"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table.setRowCount(len(users))
        for row, user in enumerate(users):
            u_id, last_name, first_name, login, role = user
            table.setItem(row, 0, QTableWidgetItem(str(u_id)))
            table.setItem(row, 1, QTableWidgetItem(str(last_name)))
            table.setItem(row, 2, QTableWidgetItem(str(first_name)))
            table.setItem(row, 3, QTableWidgetItem(str(login)))
            table.setItem(row, 4, QTableWidgetItem(str(role)))
            
        layout.addWidget(table)
        dialog.exec()

    def setup_role_interface(self):
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()
        
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:
            self.manager_button.show()
        elif self.role_id == 3:
            self.order_button.show()

    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.login_window = LoginWindow(Database())
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    db = Database()
    from login_window import LoginWindow
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())
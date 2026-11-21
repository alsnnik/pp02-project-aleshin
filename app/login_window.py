from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None

        self.setWindowTitle("Авторизация — Мир интерьера")
        self.resize(350, 300)

        # --- СТИЛИ ОКНА ---
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            /* Поле ввода: явно указываем черный цвет текста */
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #F9F9F9;
                color: #000000; 
            }
            QLineEdit:focus {
                border: 1px solid #70B2AF; /* Бирюзовая рамка при вводе */
            }
            /* Кнопка "Войти" (бирюзовая) */
            QPushButton#btnLogin {
                background-color: #70B2AF;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#btnLogin:hover {
                background-color: #5c9694;
            }
            /* Кнопка "Войти как гость" (серо-голубая) */
            QPushButton#btnGuest {
                background-color: #9BA4B5;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton#btnGuest:hover {
                background-color: #848c9c;
            }
        """)

        # --- ВЕРСТКА ---
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("Вход в систему")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #333333;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Поле логина
        layout.addWidget(QLabel("Введите ваш логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Например: admin, manager1, client01")
        layout.addWidget(self.login_input)

        # Кнопка Войти
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("btnLogin")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        # Кнопка Гость
        self.guest_button = QPushButton("Войти как Гость")
        self.guest_button.setObjectName("btnGuest")
        self.guest_button.clicked.connect(self.login_as_guest)
        layout.addWidget(self.guest_button)

        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        cursor = None
        try:
            cursor = conn.cursor()
            # Ищем пользователя по логину
            cursor.execute(
                "SELECT user_id, role_id, last_name, first_name "
                "FROM users WHERE login = %s",
                (login,)
            )
            result = cursor.fetchone()

            if result is None:
                QMessageBox.warning(self, "Ошибка", "Неверный логин")
            else:
                self.user_id = result[0]
                self.role_id = result[1]
                
                # Формируем ФИО
                last_name = result[2] if result[2] else ""
                first_name = result[3] if result[3] else ""
                self.full_name = f"{last_name} {first_name}".strip()
                if not self.full_name:
                    self.full_name = login # Если ФИО пустое, показываем логин

                # Переходим в главное окно
                from main import MainWindow
                self.main_window = MainWindow(
                    user_id=self.user_id, 
                    role_id=self.role_id, 
                    full_name=self.full_name
                )
                self.main_window.show()
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при запросе:\n{e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.db.release_connection(conn)

    def login_as_guest(self):
        from main import MainWindow
        self.main_window = MainWindow(user_id=None, role_id=None, full_name="Гость")
        self.main_window.show()
        self.close()
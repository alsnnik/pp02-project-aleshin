from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox)

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None

        self.setWindowTitle("Авторизация — Мир интерьера")
        self.resize(300, 250)

        layout = QVBoxLayout()
        
        title_label = QLabel("Вход в систему")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        # --- Кнопка гостя ---
        self.guest_button = QPushButton("Войти как гость")
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
            # ИСПРАВЛЕНО: Используем правильные колонки, которые мы создали в seed.py
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
                
                # Собираем ФИО из фамилии и имени
                last_name = result[2] if result[2] else ""
                first_name = result[3] if result[3] else ""
                self.full_name = f"{last_name} {first_name}".strip()
                if not self.full_name:
                    self.full_name = login # Если ФИО пустое, используем логин

                from main import MainWindow
                self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name)
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
        self.main_window = MainWindow(role_id=None, full_name=None)
        self.main_window.show()
        self.close()
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
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #F9F9F9;
                color: #000000; 
            }
            QLineEdit:focus {
                border: 1px solid #70B2AF; 
            }
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

    # --- ВСПОМОГАТЕЛЬНЫЙ МЕТОД ДЛЯ ОКОН (чтобы кнопки не были пустыми) ---
    def show_custom_message(self, icon_type, title, text):
        msg = QMessageBox(self)
        msg.setIcon(icon_type)
        msg.setWindowTitle(title)
        msg.setText(text)
        
        # Принудительно стилизуем кнопку, чтобы вернуть ей текст
        btn = msg.addButton("ОК", QMessageBox.ButtonRole.AcceptRole)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #000000;
                border: 1px solid #AAAAAA;
                border-radius: 4px;
                padding: 5px 20px;
                font-size: 14px;
                font-family: Calibri;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        msg.exec()

    def check_login(self):
        login = self.login_input.text().strip()

        # --- ЗАДАНИЕ 1.1: Warning для пустого логина ---
        if not login:
            self.show_custom_message(
                QMessageBox.Icon.Warning, 
                "Внимание", 
                "Поле логина не может быть пустым!"
            )
            return

        conn = self.db.get_connection()
        if conn is None:
            self.show_custom_message(
                QMessageBox.Icon.Critical, 
                "Ошибка", 
                "Нет подключения к БД"
            )
            return

        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role_id, last_name, first_name "
                "FROM users WHERE login = %s",
                (login,)
            )
            result = cursor.fetchone()

            if result is None:
                # --- ЗАДАНИЕ 1.2: Error для неверного логина ---
                self.show_custom_message(
                    QMessageBox.Icon.Critical, 
                    "Ошибка", 
                    "Пользователь не найден"
                )
            else:
                self.user_id = result[0]
                self.role_id = result[1]
                
                last_name = result[2] if result[2] else ""
                first_name = result[3] if result[3] else ""
                self.full_name = f"{last_name} {first_name}".strip()
                if not self.full_name:
                    self.full_name = login

                # --- ЗАДАНИЕ 3.1: Information для успешного входа ---
                self.show_custom_message(
                    QMessageBox.Icon.Information, 
                    "Информация", 
                    f"Добро пожаловать, {self.full_name}!"
                )

                from main import MainWindow
                self.main_window = MainWindow(
                    user_id=self.user_id, 
                    role_id=self.role_id, 
                    full_name=self.full_name
                )
                self.main_window.show()
                self.close()
        except Exception as e:
            self.show_custom_message(
                QMessageBox.Icon.Critical, 
                "Ошибка БД", 
                f"Ошибка при запросе:\n{e}"
            )
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

    # --- ЗАДАНИЕ 2.1: Warning при закрытии окна ---
    def closeEvent(self, event):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Предупреждение")
        msg.setText("Вы уверены, что хотите выйти?")
        
        btn_yes = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
        btn_no = msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        
        # Стилизуем обе кнопки
        style = """
            QPushButton {
                background-color: #E0E0E0; color: #000000;
                border: 1px solid #AAAAAA; border-radius: 4px;
                padding: 5px 20px; font-size: 14px; font-family: Calibri;
            }
            QPushButton:hover { background-color: #D0D0D0; }
        """
        btn_yes.setStyleSheet(style)
        btn_no.setStyleSheet(style)
        
        msg.exec()
        
        if msg.clickedButton() == btn_yes:
            event.accept()
        else:
            event.ignore()
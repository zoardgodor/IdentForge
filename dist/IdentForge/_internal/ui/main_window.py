import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QComboBox, QSplitter, QApplication, QMessageBox
from PySide6.QtCore import QThread, Signal
from faker import Faker
from widgets.identity_widget import IdentityWidget
from widgets.inbox_widget import InboxWidget
from widgets.message_viewer import MessageViewer
from services.mailtm_client import MailTMClient
from services.account_storage import AccountStorage

class FetchDomainsWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            domains = self.client.fetch_domains()
            self.finished.emit(domains)
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit([])

class CreateAccountWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, client, address, password):
        super().__init__()
        self.client = client
        self.address = address
        self.password = password

    def run(self):
        try:
            result = self.client.create_account(self.address, self.password)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class LoginWorker(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, client, address, password):
        super().__init__()
        self.client = client
        self.address = address
        self.password = password

    def run(self):
        try:
            self.client.login_account(self.address, self.password)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class RefreshInboxWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            messages = self.client.get_messages()
            self.finished.emit(messages)
        except Exception as e:
            self.error.emit(str(e))

class GetMessageWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, client, id):
        super().__init__()
        self.client = client
        self.id = id

    def run(self):
        try:
            message = self.client.get_message_details(self.id)
            self.finished.emit(message)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = MailTMClient()
        self.storage = AccountStorage()
        self.accounts = {}
        self.domains = []
        self.faker = Faker()
        self.threads = []
        self.is_logged_in = False
        self.setWindowTitle('IdentForge')
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        splitter = QSplitter()
        left_widget = IdentityWidget()
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        account_layout = QFormLayout()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.show_password_button = QPushButton("👁")
        self.show_password_button.setCheckable(True)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_edit)
        password_layout.addWidget(self.show_password_button)
        password_widget = QWidget()
        password_widget.setLayout(password_layout)
        self.saved_combo = QComboBox()
        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_saved_account)
        saved_layout = QHBoxLayout()
        saved_layout.addWidget(self.saved_combo)
        saved_layout.addWidget(self.delete_button)
        saved_widget = QWidget()
        saved_widget.setLayout(saved_layout)
        account_layout.addRow('Email:', self.email_edit)
        account_layout.addRow('Password:', password_widget)
        account_layout.addRow('Saved:', saved_widget)
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton('Create Temp Email')
        self.create_button.clicked.connect(self.create_account)
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login)
        self.save_button = QPushButton('Save Account')
        self.save_button.clicked.connect(self.save_account)
        self.load_button = QPushButton('Load Saved Accounts')
        self.load_button.clicked.connect(self.load_accounts)
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.load_button)
        account_widget = QWidget()
        account_layout_widget = QVBoxLayout()
        account_layout_widget.addLayout(account_layout)
        account_layout_widget.addLayout(buttons_layout)
        account_widget.setLayout(account_layout_widget)
        self.inbox_widget = InboxWidget()
        self.inbox_widget.refresh_button.clicked.connect(self.refresh_inbox)
        self.message_viewer = MessageViewer()
        self.inbox_widget.message_selected.connect(self.load_message)
        self.saved_combo.currentTextChanged.connect(self.on_saved_selected)
        right_layout.addWidget(account_widget)
        right_layout.addWidget(self.inbox_widget)
        right_layout.addWidget(self.message_viewer)
        right_widget.setLayout(right_layout)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.load_accounts()
        self.fetch_domains()

    def closeEvent(self, event):
        for thread in self.threads:
            if thread.isRunning():
                thread.wait()
        event.accept()

    def remove_worker(self, worker):
        try:
            self.threads.remove(worker)
        except ValueError:
            pass

    def fetch_domains(self):
        worker = FetchDomainsWorker(self.client)
        worker.finished.connect(self.set_domains)
        worker.finished.connect(lambda: self.remove_worker(worker))
        worker.error.connect(lambda err: self.remove_worker(worker))
        self.threads.append(worker)
        worker.start()

    def set_domains(self, domains):
        self.domains = domains

    def create_account(self):
        if not self.domains:
            QMessageBox.warning(self, 'Error', 'Domains not loaded. Please wait.')
            return
        username = self.faker.user_name()
        address = f"{username}@{self.domains[0]['domain']}"
        password = self.faker.password()
        worker = CreateAccountWorker(self.client, address, password)
        worker.finished.connect(lambda result: self.remove_worker(worker))
        worker.finished.connect(lambda result: self.on_account_created(address, password))
        worker.error.connect(lambda err: self.remove_worker(worker))
        worker.error.connect(lambda err: self.show_error(err))
        self.threads.append(worker)
        worker.start()

    def on_account_created(self, address, password):
        self.email_edit.setText(address)
        self.password_edit.setText(password)
        QMessageBox.information(self, 'Success', f'Account created\n\nEmail: {address}\nPassword: {password}')

    def toggle_password_visibility(self):
        if self.show_password_button.isChecked():
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.show_password_button.setText("🙈")
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.show_password_button.setText("👁")

    def login(self):
        address = self.email_edit.text()
        password = self.password_edit.text()
        if not address or not password:
            QMessageBox.warning(self, 'Error', 'Email and password cannot be empty')
            return
        worker = LoginWorker(self.client, address, password)
        worker.finished.connect(lambda: self.remove_worker(worker))
        worker.finished.connect(self.on_login_success)
        worker.error.connect(lambda err: self.remove_worker(worker))
        worker.error.connect(lambda err: self.show_error(err))
        self.threads.append(worker)
        worker.start()

    def on_login_success(self):
        self.is_logged_in = True
        QMessageBox.information(self, 'Success', 'Logged in successfully')

    def save_account(self):
        email = self.email_edit.text()
        password = self.password_edit.text()
        if not email or not password:
            QMessageBox.warning(self, 'Error', 'Email and password cannot be empty')
            return
        self.storage.save_account(email, password)
        self.load_accounts()
        QMessageBox.information(self, 'Success', 'Account saved successfully')

    def load_accounts(self):
        self.accounts = self.storage.load_accounts()
        self.saved_combo.clear()
        self.saved_combo.addItems(self.accounts.keys())

    def on_saved_selected(self, email):
        if email in self.accounts:
            self.email_edit.setText(email)
            self.password_edit.setText(self.accounts[email])
            self.inbox_widget.message_list.clear()
            self.message_viewer.sender_label.setText('')
            self.message_viewer.subject_label.setText('')
            self.message_viewer.date_label.setText('')
            self.message_viewer.body_edit.setPlainText('')
            self.is_logged_in = False

    def delete_saved_account(self):
        email = self.saved_combo.currentText()
        if not email:
            QMessageBox.warning(self, 'Error', 'No account selected')
            return
        reply = QMessageBox.question(self, 'Confirm', f'Delete {email}?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.storage.delete_account(email)
            self.load_accounts()
            QMessageBox.information(self, 'Success', 'Account deleted successfully')

    def refresh_inbox(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, 'Error', 'Error: Not logged in')
            return
        worker = RefreshInboxWorker(self.client)
        worker.finished.connect(self.inbox_widget.set_messages)
        worker.finished.connect(lambda: self.remove_worker(worker))
        worker.error.connect(lambda err: self.remove_worker(worker))
        worker.error.connect(lambda err: self.show_error(err))
        self.threads.append(worker)
        worker.start()

    def load_message(self, id):
        if not self.is_logged_in:
            QMessageBox.warning(self, 'Error', 'Error: Not logged in')
            return
        worker = GetMessageWorker(self.client, id)
        worker.finished.connect(self.message_viewer.display_message)
        worker.finished.connect(lambda: self.remove_worker(worker))
        worker.error.connect(lambda err: self.remove_worker(worker))
        worker.error.connect(lambda err: self.show_error(err))
        self.threads.append(worker)
        worker.start()

    def show_error(self, error):
        QMessageBox.critical(self, 'Error', f'Error: {error}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
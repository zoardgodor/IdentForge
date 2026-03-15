from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal

class InboxWidget(QWidget):
    message_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.refresh_button = QPushButton('Refresh Inbox')
        self.message_list = QListWidget()
        self.message_list.itemClicked.connect(self.on_message_selected)
        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.message_list)
        self.setLayout(self.layout)
        self.messages = []

    def set_messages(self, messages):
        self.messages = messages
        self.message_list.clear()
        for msg in messages:
            item = QListWidgetItem(f"{msg['from']['address']} - {msg['subject']} - {msg['createdAt']}")
            item.setData(1, msg['id'])
            self.message_list.addItem(item)

    def on_message_selected(self, item):
        msg_id = item.data(1)
        self.message_selected.emit(msg_id)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class MessageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.sender_label = QLabel()
        self.subject_label = QLabel()
        self.date_label = QLabel()
        self.body_edit = QTextEdit()
        self.body_edit.setReadOnly(True)
        self.layout.addWidget(self.sender_label)
        self.layout.addWidget(self.subject_label)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.body_edit)
        self.setLayout(self.layout)

    def display_message(self, message):
        self.sender_label.setText(f"From: {message['from']['address']}")
        self.subject_label.setText(f"Subject: {message['subject']}")
        self.date_label.setText(f"Date: {message['createdAt']}")
        self.body_edit.setPlainText(message.get('text', '') or message.get('html', ''))
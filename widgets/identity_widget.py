from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFormLayout, QLineEdit
from services.fake_identity import FakeIdentity

class IdentityWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.generate_button = QPushButton('Generate Identity')
        self.generate_button.clicked.connect(self.generate_identity)
        self.form_layout = QFormLayout()
        self.fields = {}
        fields = ['name', 'username', 'gender', 'address', 'city', 'country', 'zip_code', 'phone', 'birthdate', 'job_title']
        for field in fields:
            label = QLabel(field.capitalize() + ':')
            value_edit = QLineEdit()
            value_edit.setReadOnly(True)
            self.form_layout.addRow(label, value_edit)
            self.fields[field] = value_edit
        self.layout.addWidget(self.generate_button)
        self.layout.addLayout(self.form_layout)
        self.setLayout(self.layout)

    def generate_identity(self):
        identity = FakeIdentity.generate()
        for field, value in identity.items():
            self.fields[field].setText(str(value))
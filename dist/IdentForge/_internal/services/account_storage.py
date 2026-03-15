import json
import os

class AccountStorage:
    def __init__(self, file_path=None):
        if file_path is None:
            appdata = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming')
            identforge_dir = os.path.join(appdata, 'IdentForge')
            os.makedirs(identforge_dir, exist_ok=True)
            file_path = os.path.join(identforge_dir, 'accounts.json')
        self.file_path = file_path

    def save_account(self, email, password):
        accounts = self.load_accounts()
        accounts[email] = password
        with open(self.file_path, 'w') as f:
            json.dump(accounts, f)

    def load_accounts(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {}

    def delete_account(self, email):
        accounts = self.load_accounts()
        if email in accounts:
            del accounts[email]
            with open(self.file_path, 'w') as f:
                json.dump(accounts, f)
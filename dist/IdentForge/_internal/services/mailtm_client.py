import requests

class MailTMClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def fetch_domains(self):
        response = self.session.get('https://api.mail.tm/domains')
        response.raise_for_status()
        return response.json()['hydra:member']

    def create_account(self, address, password):
        data = {'address': address, 'password': password}
        response = self.session.post('https://api.mail.tm/accounts', json=data)
        response.raise_for_status()
        return response.json()

    def login_account(self, address, password):
        data = {'address': address, 'password': password}
        response = self.session.post('https://api.mail.tm/token', json=data)
        response.raise_for_status()
        self.token = response.json()['token']
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})
        return self.token

    def get_messages(self):
        response = self.session.get('https://api.mail.tm/messages')
        response.raise_for_status()
        return response.json()['hydra:member']

    def get_message_details(self, id):
        response = self.session.get(f'https://api.mail.tm/messages/{id}')
        response.raise_for_status()
        return response.json()
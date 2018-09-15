import requests

class Client:
    LOGIN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

    def __init__(self, refresh_token, account_id):
        self.login_response = self.__login(refresh_token)
        self.account_id = account_id

    def __login(self, refresh_token):
        response = requests.get(self.LOGIN_URL + refresh_token)
        response.raise_for_status()
        config = response.json()
        self.api_server = config["api_server"] + 'v1/'
        self.header = { "authorization":
                f"{config['token_type']} {config['access_token']}" }
        return config

    def get_accounts(self):
        return self.get("accounts")

    def get_balances(self):
        return self.get(f"accounts/{self.account_id}/balances")

    def get_positions(self):
        return self.get(f"accounts/{self.account_id}/positions")

    def get_symbol(self, symbol):
        return self.get("symbols", params={'names': symbol})

    def get_quote(self, symbol_id):
        return self.get(f"markets/quotes/{symbol_id}")

    def get(self, path, params=None):
        return self.get_raw(path, params).json()

    def get_raw(self, path, params=None):
        response = requests.get(self.api_server + path,
                                headers=self.header, params=params)
        response.raise_for_status()
        return response

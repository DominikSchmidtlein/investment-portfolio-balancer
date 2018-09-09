import requests
import functools

class Client:
    LOGIN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

    def __init__(self, refresh_token, account_id):
        self.login_response = self.__login(refresh_token)
        self.account_id = account_id

    def __login(self, refresh_token):
        config = self.get(self.LOGIN_URL + refresh_token, headers={})
        self.api_server = config["api_server"]
        self.authorization = config['token_type'] + ' ' + config['access_token']
        return config

    def get_accounts(self):
        url = "{s.api_server}v1/accounts".format(s=self)
        return self.get(url)

    def get_balances(self):
        url = "{s.api_server}v1/accounts/{s.account_id}/balances".format(s=self)
        return self.get(url)

    def get_positions(self):
        url = "{s.api_server}v1/accounts/{s.account_id}/positions".format(s=self)
        return self.get(url)

    def get_symbol(self, symbol):
        url = "{s.api_server}v1/symbols".format(s=self)
        return self.get(url, params={'names': symbol})

    def get_quote(self, symbol_id):
        url = "{s.api_server}v1/markets/quotes/{symbol_id}".format(s=self, symbol_id=symbol_id)
        return self.get(url)

    def get(self, url, headers=None, params=None):
        if headers is None:
            headers = { "authorization": self.authorization }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def __post_request_headers(self):
        return {
            "authorization": self.authorization,
            "Content-Type": "application/json"
        }

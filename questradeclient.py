import requests

class QuestradeClient:
	LOGIN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

	def __init__(self, refresh_token, account_id):
		self.login_response = self.__login(refresh_token)
		self.account_id = account_id

	def __login(self, refresh_token):
		response = requests.get(self.LOGIN_URL + refresh_token)
		response.raise_for_status()
		config = response.json()
		self.api_server = config["api_server"]
		self.authorization = config['token_type'] + ' ' + config['access_token']
		return config

	def get_accounts(self):
		url = "{s.api_server}v1/accounts".format(s=self)
		response = requests.get(url, headers=self.__get_request_headers())
		response.raise_for_status()
		return response.json()

	def get_balances(self, raw=True, currencies=None, attributes=None):
		url = "{s.api_server}v1/accounts/{s.account_id}/balances".format(s=self)
		response = requests.get(url, headers=self.__get_request_headers())
		response.raise_for_status()
		json = response.json()
		if raw:
			return json
		elif not currencies and not attributes:
			return json["perCurrencyBalances"]
		return map(lambda c: { k: v for k, v in c.items() if k in attributes },
			filter(lambda c: c['currency'] in currencies, json["perCurrencyBalances"]))

	def get_positions(self, raw=True, attributes=None):
		url = "{s.api_server}v1/accounts/{s.account_id}/positions".format(s=self)
		response = requests.get(url, headers=self.__get_request_headers())
		response.raise_for_status()
		json = response.json()
		if raw:
			return json
		elif not attributes:
			return json['positions']
		return map(lambda p: { k: v for k, v in p.items() if k in attributes },
			json['positions'])

	def market_purchase(self, symbolId, quantity):
		if quantity <= 0:
			return
		data = {
			"symbolId": symbolId,
			"quantity": quantity,
			"timeInForce": "Day",
			"icebergQuantity": 10,
			"isAllOrNone": False,
			"orderType": "Market",
			"action": "Buy",
			"primaryRoute": "AUTO",
			"secondaryRoute": "AUTO",
		}
		url = "{s.api_server}v1/accounts/{s.account_id}/orders".format(s=self)
		response = requests.post(url, headers=self.__post_request_headers(), json=data)
		response.raise_for_status()
		return response.json()

	def __get_request_headers(self):
		return {
			"authorization": self.authorization
		}

	def __post_request_headers(self):
		return {
			"authorization": self.authorization,
			"Content-Type": "application/json"
		}

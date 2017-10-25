import requests

class QuestradeClient:
	LOGIN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

	def __init__(self, refresh_token, account_id):
		self.__login_response = self.__login(refresh_token)
		self.__account_id = account_id

	def __login(self, refresh_token):
		response = requests.get(self.LOGIN_URL + refresh_token)
		response.raise_for_status()
		config = response.json()
		self.__api_server = config["api_server"]
		self.__authorization = config['token_type'] + ' ' + config['access_token']
		return config

	def login_response(self):
		return self.__login_response

	def get_accounts(self):
		url = "{s.__api_server}v1/accounts".format(s=self)
		response = requests.get(url, headers=self.__get_request_headers())
		response.raise_for_status()
		return response.json()

	def get_balances(self):
		url = "{s.__api_server}v1/accounts/{s.__account_id}/balances".format(s=self)
		response = requests.get(url, headers=self.__get_request_headers())
		response.raise_for_status()
		return response.json()

	def get_positions(self):
		url = "{s.__api_server}v1/accounts/{s.__account_id}/positions".format(s=self)
		response = requests.get(url, headers=self.__get_request_headers())
		response.raise_for_status()
		return response.json()

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
		url = "{s.__api_server}v1/accounts/{s.__account_id}/orders".format(s=self)
		response = requests.post(url, headers=self.__post_request_headers(), json=data)
		response.raise_for_status()
		return response.json()

	def __get_request_headers(self):
		return {
			"authorization": self.__authorization
		}

	def __post_request_headers(self):
		return {
			"authorization": self.__authorization,
			"Content-Type": "application/json"
		}

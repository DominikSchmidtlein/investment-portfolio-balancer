import requests

class QuestradeClient:
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

	def get_balances(self, raw=True, currencies=None, attributes=None):
		url = "{s.api_server}v1/accounts/{s.account_id}/balances".format(s=self)
		json = self.get(url)
		if raw:
			return json
		elif not currencies and not attributes:
			return json["perCurrencyBalances"]
		return [{ k: v for k, v in c.items() if k in attributes }
			for c in (c for c in json["perCurrencyBalances"] if c['currency'] in currencies)]

	def get_positions(self, raw=True, attributes=None):
		url = "{s.api_server}v1/accounts/{s.account_id}/positions".format(s=self)
		json = self.get(url)
		if raw:
			return json
		elif not attributes:
			return json['positions']
		return { p['symbol']: { k: v for k, v in p.items() if k in attributes } for p in json['positions'] }

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

	def get_symbol(self, symbol, attributes=None):
		url = "{s.api_server}v1/symbols".format(s=self)
		json = self.get(url, params={'names': symbol})['symbols'][0]
		if not attributes:
			return json
		else:
			return { k: v for k, v in json.items() if k in attributes }

	def get_quote(self, symbol_id, attributes=None):
		url = "{s.api_server}v1/markets/quotes/{symbol_id}".format(s=self, symbol_id=symbol_id)
		json = self.get(url)['quotes'][0]
		if not attributes:
			return json
		else:
			return { k: v for k, v in json.items() if k in attributes }

	def get(self, url, headers=None, params=None):
		if headers is None:
			headers = self.__get_request_headers()
		response = requests.get(url, headers=headers, params=params)
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

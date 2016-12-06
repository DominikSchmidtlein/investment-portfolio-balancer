import requests
import pdb

class QuestradeAPI:
	login_url = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

	def __init__(self, refresh_token):
		self.refresh_token = refresh_token
		
	def login(self):
		response = requests.get(self.login_url + self.refresh_token)
		response.raise_for_status()
		config = response.json()

		self.api_server = config["api_server"]
		self.accounts_url = self.api_server + "v1/accounts"
		
		token_type = config["token_type"]
		access_token = config["access_token"]
		self.get_headers = {
			"authorization": "%s %s" % (token_type, access_token)
		}
		self.post_headers = {
			"authorization": self.get_headers["authorization"],
			"Content-Type": "application/json"
		}
		return config

	def set_account(self, account_id):
		self.account_id = account_id
		self.account_id_url = self.accounts_url + "/" + self.account_id
		self.positions_url = self.account_id_url + "/positions"
		self.balances_url = self.account_id_url + "/balances"
		self.orders_url = self.account_id_url + "/orders"

	def get_accounts(self):
		response = requests.get(self.accounts_url, headers=self.get_headers)
		response.raise_for_status()
		return response.json()

	def get_balances(self):
		response = requests.get(self.balances_url, headers=self.get_headers)
		response.raise_for_status()
		return response.json()

	def get_positions(self):
		response = requests.get(self.positions_url, headers=self.get_headers)
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
		response = requests.post(self.orders_url, headers=self.post_headers, json=data)
		pdb.set_trace()
		response.raise_for_status()
		return response.json()
		


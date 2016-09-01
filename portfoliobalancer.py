import requests
import json

class PortfolioBalancer:

	def __init__(self):
		self.configFileHandler = ConfigFileHandler(".config")

	def balance(self):
		load_config()
		questrade_login()
		
		PortfolioCalculator(portfolio).calculate()
		PortfolioPrinter(portfolio).print_all()

	def load_config(self):
		config = configFileHandler.load()
		self.account_id = config["account_id"]
		self.refresh_token = config["refresh_token"]

	def questrade_login(self):
		self.questradeAPI = QuestradeAPI(account_id)
		config = questradeAPI.login(refresh_token)
		configFileHandler.save(config)

	def get_portfolio(self):
		self.portfolio = questradeAPI.get_positions()
		balances = questradeAPI.get_balances()["perCurrencyBalances"][0]
		portfolio["cash"] = balances["cash"]
		portfolio["marketValue"] = balances["marketValue"]
		portfolio["totalEquity"] = balances["totalEquity"]

class PortfolioCalculator:

	composition = {
	  "VE.TO": 23,
	  "VA.TO": 15,
	  "VEE.TO": 11,
	  "VCN.TO": 4,
	  "VUN.TO": 47
	}
	assert sum(composition.itervalues()) == 100

	def __init__(self, portfolio):
		self.portfolio = portfolio

	def check_portfolio(self):
		assert isinstance(self.portfolio["cash"], float)
		assert self.portfolio["cash"] >= 0
		assert self.portfolio["marketValue"] >= 0
		assert self.portfolio["totalEquity"] >= 0
		assert abs(self.portfolio["totalEquity"] - self.portfolio["marketValue"] - self.portfolio["cash"]) < 0.01

	def calculate_percentage(self):
		for position in self.portfolio["positions"]:
			position["percentage"] = composition[position["symbol"]] / 100.0

	def calculate_theoretical(self):
		self.portfolio["theoreticalTotalEquity"] = self.portfolio["totalEquity"]
		for position in self.portfolio["positions"]:
			position["theoreticalQuantity"] = self.portfolio["totalEquity"] * position["percentage"] / position["currentPrice"]
			position["theoreticalValue"] = position["theoreticalQuantity"] * position["currentPrice"]
			self.portfolio["theoreticalMarketValue"] += position["theoreticalValue"]
		self.portfolio["theoreticalCash"] = self.portfolio["theoreticalTotalEquity"] - self.portfolio["theoreticalMarketValue"]

	def calculate_purchases(self):
		for position in self.portfolio["positions"]:
			position["purchaseQuantity"] = round(max(position["theoreticalQuantity"] - position["openQuantity"], 0), -1)
			position["purchaseValue"] = position["purchaseQuantity"] * position["currentPrice"]

	def calculate_practical(self):
		self.portfolio["practicalTotalEquity"] = self.portfolio["totalEquity"]
		for position in self.portfolio["positions"]:
			position["practicalQuantity"] = position["openQuantity"] + position["purchaseQuantity"]
			position["practicalValue"] = position["practicalQuantity"] * position["currentPrice"]
			self.portfolio["practicalMarketValue"] += position["practicalValue"]
		self.portfolio["practicalCash"] = self.portfolio["practicalTotalEquity"] - self.portfolio["practicalMarketValue"]

	def check_calculations(self):
		assert abs(self.portfolio["theoreticalCash"]) < 0.01
		assert self.portfolio["practicalCash"] >= 0
		assert abs(self.portfolio["theoreticalMarketValue"] - self.portfolio["theoreticalTotalEquity"]) < 0.01
		assert abs(self.portfolio["totalEquity"] - self.portfolio["theoreticalTotalEquity"]) < 0.01
		assert abs(self.portfolio["totalEquity"] - self.portfolio["practicalTotalEquity"]) < 0.01

	def calculate(self):
		check_portfolio()
		calculate_percentage()
		calculate_theoretical()
		calculate_purchases()
		calculate_practical()
		check_calculations()

class ConfigFileHandler:
	def __init__(self, filename):
		self.filename = filename

	def load(self):
		with open(filename, "r") as f:
			return json.loads(f.read())

	def save(self, config):
		with open(filename, "w") as f:
			f.write(config)

class QuestradeAPI:
	login_url = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

	def __init__(self, account_id):
		self.account_id = account_id
		
	def login(self, refresh_token):
		response = requests.get(login_url + refresh_token)
		response.raise_for_status()
		config = response.json()

		api_server = config["api_server"]
		account_id_url = api_server + "v1/accounts/" + account_id
		self.positions_url = account_id_url + "/positions"
		self.balances_url = account_id_url + "/balances"

		token_type = config["token_type"]
		access_token = config["access_token"]
		self.headers = {
			"authorization": "%s %s" % (token_type, access_token)
		}

		config["account_id"] = account_id
		return config

	def get_balances(self):
		response = requests.get(self.balances_url, headers=self.headers)
		response.raise_for_status()
		return response.json()

	def get_positions(self):
		response = requests.get(self.positions_url, headers=self.headers)
		response.raise_for_status()
		return response.json()

class PortfolioPrinter:
	template = "{bound}{pad}{field1:{filler}<{w1}}{pad}{bound}{pad}{field2:{filler}>{w2}}{pad}{bound}"
	def __init__(self, portfolio):
		self.portfolio = portfolio

	def print_all(self):
		print_purchases()
		print_balances()

	def print_purchases(self):
		w1 = 10
		w2 = 10
		print "Purchases:"
		print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print template.format(bound="|",pad=" ",filler=" ",field1="Symbol",field2="Quantity",w1=w1,w2=w2)
		print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		for position in portfolio["positions"]:
			print template.format(bound="|",pad=" ",filler=" ",field1=position["symbol"],field2=position["purchaseQuantity"],w1=w1,w2=w2)
		print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print ""

	def print_balances(self):
		w1 = 15
		w2 = 15
		print "Post Purchase Balances:"
		print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print template.format(bound="|",pad=" ",filler=" ",field1="Balance",field2="Value",w1=w1,w2=w2)
		print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print template.format(bound="|",pad=" ",filler=" ",field1="Cash",field2=portfolio["practicalCash"],w1=w1,w2=w2)
		print template.format(bound="|",pad=" ",filler=" ",field1="Market Value",field2=portfolio["practicalMarketValue"],w1=w1,w2=w2)
		print template.format(bound="|",pad=" ",filler=" ",field1="Total Equity",field2=portfolio["practicalTotalEquity"],w1=w1,w2=w2)
		print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print ""

def main():
	PortfolioBalancer().balance()

if __name__ == '__main__':
	main()

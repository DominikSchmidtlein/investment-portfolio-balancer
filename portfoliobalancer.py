import requests
import json
import sys

class PortfolioBalancer:

	def __init__(self):
		self.configFileHandler = ConfigFileHandler(".config")

	def balance(self):
		if len(sys.argv) == 3:
			self.use_argv()
		else:
			self.load_config()
		self.questrade_login()
		self.get_portfolio()		
		PortfolioCalculator(self.portfolio).calculate()
		PortfolioPrinter(self.portfolio).print_all()

	def use_argv(self):
		self.account_id = sys.argv[1]
		self.refresh_token = sys.argv[2]

	def load_config(self):
		config = self.configFileHandler.load()
		self.account_id = config["account_id"]
		self.refresh_token = config["refresh_token"]

	def questrade_login(self):
		self.questradeAPI = QuestradeAPI(self.account_id)
		config = self.questradeAPI.login(self.refresh_token)
		self.configFileHandler.save(json.dumps(config))

	def get_portfolio(self):
		self.portfolio = self.questradeAPI.get_positions()
		balances = self.questradeAPI.get_balances()["perCurrencyBalances"][0]
		self.portfolio["cash"] = balances["cash"]
		self.portfolio["marketValue"] = balances["marketValue"]
		self.portfolio["totalEquity"] = balances["totalEquity"]

class PortfolioCalculator:

	composition = {
	  "VE.TO": 23,
	  "VA.TO": 15,
	  "VEE.TO": 11,
	  "VCN.TO": 4,
	  "VUN.TO": 47
	}
	# assert sum(composition.itervalues()) == 100

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
			position["percentage"] = self.composition[position["symbol"]] / 100.0

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
		self.check_portfolio()
		self.calculate_percentage()
		self.calculate_theoretical()
		self.calculate_purchases()
		self.calculate_practical()
		self.check_calculations()

class ConfigFileHandler:
	def __init__(self, filename):
		self.filename = filename

	def load(self):
		with open(self.filename, "r") as f:
			return json.loads(f.read())

	def save(self, config):
		with open(self.filename, "w") as f:
			f.write(config)

class QuestradeAPI:
	login_url = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

	def __init__(self, account_id):
		self.account_id = account_id
		
	def login(self, refresh_token):
		response = requests.get(self.login_url + refresh_token)
		response.raise_for_status()
		config = response.json()

		api_server = config["api_server"]
		account_id_url = api_server + "v1/accounts/" + self.account_id
		self.positions_url = account_id_url + "/positions"
		self.balances_url = account_id_url + "/balances"

		token_type = config["token_type"]
		access_token = config["access_token"]
		self.headers = {
			"authorization": "%s %s" % (token_type, access_token)
		}

		config["account_id"] = self.account_id
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
		self.print_purchases()
		self.print_balances()

	def print_purchases(self):
		w1 = 10
		w2 = 10
		print "Purchases:"
		print self.template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print self.template.format(bound="|",pad=" ",filler=" ",field1="Symbol",field2="Quantity",w1=w1,w2=w2)
		print self.template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		for position in self.portfolio["positions"]:
			print self.template.format(bound="|",pad=" ",filler=" ",field1=position["symbol"],field2=position["purchaseQuantity"],w1=w1,w2=w2)
		print self.template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print ""

	def print_balances(self):
		w1 = 15
		w2 = 15
		print "Post Purchase Balances:"
		print self.template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print self.template.format(bound="|",pad=" ",filler=" ",field1="Balance",field2="Value",w1=w1,w2=w2)
		print self.template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print self.template.format(bound="|",pad=" ",filler=" ",field1="Cash",field2=self.portfolio["practicalCash"],w1=w1,w2=w2)
		print self.template.format(bound="|",pad=" ",filler=" ",field1="Market Value",field2=self.portfolio["practicalMarketValue"],w1=w1,w2=w2)
		print self.template.format(bound="|",pad=" ",filler=" ",field1="Total Equity",field2=self.portfolio["practicalTotalEquity"],w1=w1,w2=w2)
		print self.template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
		print ""

def main():
	PortfolioBalancer().balance()

if __name__ == '__main__':
	main()

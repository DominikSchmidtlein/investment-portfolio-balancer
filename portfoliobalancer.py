import json
import sys
from configfilehandler import *
from portfolioprinter import *
from portfoliocalculator import *
from questradeapi import *

class PortfolioBalancer:

	def __init__(self):
		self.configFileHandler = ConfigFileHandler(".config")

	def balance(self):
		if len(sys.argv) == 2:
			self.refresh_token = sys.argv[1].rstrip()
		else:
			self.refresh_token = self.configFileHandler.load_refresh_token()
		self.questrade_login()
		self.select_account()
		self.get_portfolio()
		PortfolioCalculator(self.portfolio).calculate()
		PortfolioPrinter(self.portfolio).print_all()
		self.place_oders()

	def questrade_login(self):
		self.questradeAPI = QuestradeAPI(self.refresh_token)
		config = self.questradeAPI.login()
		self.configFileHandler.save(json.dumps(config))

	def select_account(self):
		accounts = self.questradeAPI.get_accounts()["accounts"]
		for account in accounts:
			if account["type"] == "TFSA" and account["isPrimary"]:
				self.questradeAPI.set_account(account["number"])
				break

	def get_portfolio(self):
		self.portfolio = self.questradeAPI.get_positions()
		balances = self.questradeAPI.get_balances()["perCurrencyBalances"][0]
		self.portfolio["cash"] = balances["cash"]
		self.portfolio["marketValue"] = balances["marketValue"]
		self.portfolio["totalEquity"] = balances["totalEquity"]

	def place_oders(self):
		for position in self.portfolio["positions"]:
			response = self.questradeAPI.market_purchase(position["symbolId"], position["practicalPurchaseQuantity"])

def main():
	PortfolioBalancer().balance()

if __name__ == '__main__':
	main()

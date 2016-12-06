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
			position["percentage"] = self.composition[position["symbol"]] / 100.0

	def calculate_theoretical(self):
		self.portfolio["theoreticalTotalEquity"] = self.portfolio["totalEquity"]
		self.portfolio["theoreticalMarketValue"] = 0
		for position in self.portfolio["positions"]:
			position["theoreticalQuantity"] = max(self.portfolio["totalEquity"] * position["percentage"] / position["currentPrice"], 0)
			position["theoreticalValue"] = position["theoreticalQuantity"] * position["currentPrice"]
			position["theoreticalPurchaseQuantity"] = max(position["theoreticalQuantity"] - position["openQuantity"], 0)
			position["theoreticalPurchaseValue"] = position["theoreticalPurchaseQuantity"] * position["currentPrice"]
			self.portfolio["theoreticalMarketValue"] += position["theoreticalValue"]
		self.portfolio["theoreticalCash"] = self.portfolio["theoreticalTotalEquity"] - self.portfolio["theoreticalMarketValue"]

	def calculate_purchases(self):
		# confirm all purchases of multiples of 10
		self.portfolio["practicalCash"] = self.portfolio["cash"]
		for position in self.portfolio["positions"]:
			position["practicalPurchaseQuantity"] = int(position["theoreticalPurchaseQuantity"]) / 10 * 10
			position["practicalPurchaseValue"] = position["practicalPurchaseQuantity"] * position["currentPrice"]
			self.portfolio["practicalCash"] -= position["practicalPurchaseValue"]
			position["remainingPurchaseQuantity"] = position["theoreticalPurchaseQuantity"] % 10
		#sort by remainingPurchaseQuantity
		self.portfolio["positions"].sort(key=lambda position: position["remainingPurchaseQuantity"], reverse=True)
		for position in self.portfolio["positions"]:
			if self.portfolio["practicalCash"] > 10 * position["currentPrice"]:
				position["practicalPurchaseQuantity"] += 10
				position["practicalPurchaseValue"] += 10 * position["currentPrice"]
				self.portfolio["practicalCash"] -= 10 * position["currentPrice"]
				position["remainingPurchaseQuantity"] -= 10

	def calculate_practical(self):
		self.portfolio["practicalTotalEquity"] = self.portfolio["totalEquity"]
		self.portfolio["practicalMarketValue"] = 0
		for position in self.portfolio["positions"]:
			position["practicalQuantity"] = position["openQuantity"] + position["practicalPurchaseQuantity"]
			position["practicalValue"] = position["practicalQuantity"] * position["currentPrice"]
			self.portfolio["practicalMarketValue"] += position["practicalValue"]
		# self.portfolio["practicalCash"] = self.portfolio["practicalTotalEquity"] - self.portfolio["practicalMarketValue"]

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

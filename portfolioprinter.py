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
			print self.template.format(bound="|",pad=" ",filler=" ",field1=position["symbol"],field2=position["practicalPurchaseQuantity"],w1=w1,w2=w2)
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

import requests
import json

login_url = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="
composition = {
  "VE.TO": 23,
  "VA.TO": 15,
  "VEE.TO": 11,
  "VCN.TO": 4,
  "VUN.TO": 47
}
assert sum(composition.itervalues()) == 100

with open("login_response.txt", "r") as f:
	account_id = f.readline().rstrip()
	login_response = json.loads(f.readline())

refresh_token = login_response["refresh_token"]
response = requests.get(login_url + refresh_token)
response.raise_for_status()

with open("login_response.txt", "w") as f:
	f.write("%s\n%s" % (account_id, response.text))

login_response = response.json()

access_token = login_response["access_token"]
refresh_token = login_response["refresh_token"]
api_server = login_response["api_server"]
token_type = login_response["token_type"]

account_id_url = api_server + "v1/accounts/" + account_id
positions_url = account_id_url + "/positions"
balances_url = account_id_url + "/balances"

headers = {"authorization":"%s %s" % (token_type, access_token)}
response = requests.get(positions_url, headers=headers)
response.raise_for_status()
etfs = response.json()

response = requests.get(balances_url, headers=headers)
response.raise_for_status()
balances = response.json()

etfs["cash"] = balances["perCurrencyBalances"][0]["cash"]
etfs["marketValue"] = balances["perCurrencyBalances"][0]["marketValue"]
etfs["totalEquity"] = balances["perCurrencyBalances"][0]["totalEquity"]

print etfs["cash"]
print etfs["marketValue"]
print etfs["totalEquity"]

assert isinstance(etfs["cash"], float)
assert etfs["cash"] >= 0
assert etfs["marketValue"] >= 0
assert etfs["totalEquity"] >= 0
assert abs(etfs["totalEquity"] - etfs["marketValue"] - etfs["cash"]) <= 0.01

etfs["theoreticalMarketValue"] = 0
etfs["theoreticalTotalEquity"] = etfs["totalEquity"]

etfs["practicalMarketValue"] = 0
etfs["practicalTotalEquity"] = etfs["totalEquity"]


# etfs["totalEquity"] += 1000

for position in etfs["positions"]:
	position["percentage"] = composition[position["symbol"]] / 100.0

	position["theoreticalQuantity"] = etfs["totalEquity"] * position["percentage"] / position["currentPrice"]
	position["theoreticalValue"] = position["theoreticalQuantity"] * position["currentPrice"]
	etfs["theoreticalMarketValue"] += position["theoreticalValue"]

	position["purchaseQuantity"] = round(max(position["theoreticalQuantity"] - position["openQuantity"], 0), -1)
	position["purchaseValue"] = position["purchaseQuantity"] * position["currentPrice"]

	position["practicalQuantity"] = position["openQuantity"] + position["purchaseQuantity"]
	position["practicalValue"] = position["practicalQuantity"] * position["currentPrice"]
	etfs["practicalMarketValue"] += position["practicalValue"]

etfs["theoreticalCash"] = etfs["theoreticalTotalEquity"] - etfs["theoreticalMarketValue"]
etfs["practicalCash"] = etfs["practicalTotalEquity"] - etfs["practicalMarketValue"]

assert etfs["theoreticalCash"] == 0
assert etfs["practicalCash"] >= 0
assert etfs["theoreticalMarketValue"] == etfs["theoreticalTotalEquity"]
assert etfs["totalEquity"] == etfs["theoreticalTotalEquity"]
assert etfs["totalEquity"] == etfs["practicalTotalEquity"]

template = "{bound}{pad}{field1:{filler}<{w1}}{bound}{pad}{field2:{filler}>{w2}}{bound}"
w1 = 10
w2 = 10
print "Purchases:"
print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
print template.format(bound="|",pad=" ",filler=" ",field1="Symbol",field2="Quantity",w1=w1,w2=w2)
print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
for position in etfs["positions"]:
	print template.format(bound="|",pad=" ",filler=" ",field1=position["symbol"],field2=position["purchaseQuantity"],w1=w1,w2=w2)
print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
print ""
w1 = 15
w2 = 15
print "Post Purchase Balances:"
print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
print template.format(bound="|",pad=" ",filler=" ",field1="Balance",field2="Value",w1=w1,w2=w2)
print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)
print template.format(bound="|",pad=" ",filler=" ",field1="Cash",field2=etfs["practicalCash"],w1=w1,w2=w2)
print template.format(bound="|",pad=" ",filler=" ",field1="Market Value",field2=etfs["practicalMarketValue"],w1=w1,w2=w2)
print template.format(bound="|",pad=" ",filler=" ",field1="Total Equity",field2=etfs["practicalTotalEquity"],w1=w1,w2=w2)
print template.format(bound="+",pad="-",filler="-",field1="",field2="",w1=w1,w2=w2)

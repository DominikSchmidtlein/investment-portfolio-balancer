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
assert isinstance(etfs["cash"], float)

# etfs["totalEquity"] += 1000
sum_theoretical_value = 0

for position in etfs["positions"]:
	position["percentage"] = composition[position["symbol"]] / 100.0
	position["theoreticalQuantity"] = etfs["totalEquity"] * position["percentage"] / position["currentPrice"]
	position["theoreticalValue"] = position["theoreticalQuantity"] * position["currentPrice"]
	position["purchaseQuantity"] = round(max(position["theoreticalQuantity"] - position["openQuantity"], 0), -1)
	position["purchaseValue"] = position["purchaseQuantity"] * position["currentPrice"]
	
	sum_theoretical_value += position["theoreticalValue"]

	print position["symbol"]
	print position["openQuantity"]
	print position["theoreticalQuantity"]
	print position["purchaseQuantity"]

print "Sum of theoretical values: ", sum_theoretical_value
print "Total equity: ", etfs["totalEquity"]

import requests
import json

account_id = ""
login_url = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="
ratios = {
  "VE.TO": 23,
  "VA.TO": 15,
  "VEE.TO": 11,
  "VCN.TO": 4,
  "VUN.TO": 47
}
assert sum(ratios.itervalues()) == 100

f = open("login_response.txt", "r")

account_id = f.readline()
login_response = json.loads(f.readline())
f.close()

refresh_token = login_response["refresh_token"]
response = requests.get(login_url + refresh_token)
assert response.status_code/100 == 2

f = open("login_response.txt", "w")
f.write("%s\n%s" % (account_id, response.text))
f.close()

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
assert response.status_code/100 == 2
etfs = response.json()

response = requests.get(balances_url, headers=headers)
assert response.status_code/100 == 2
balances = response.json()

etfs["cash"] = balances["perCurrencyBalances"][0]["cash"]
etfs["marketValue"] = balances["perCurrencyBalances"][0]["marketValue"]
etfs["totalEquity"] = balances["perCurrencyBalances"][0]["totalEquity"]
assert isinstance(etfs["cash"], float)

# etfs["totalEquity"] += 1000

for position in etfs["positions"]:
	position["ratio"] = ratios[position["symbol"]]
	position["potentialQuantity"] = etfs["totalEquity"] * position["ratio"] / 100.0 / position["currentPrice"]
	position["purchaseQuantity"] = int(max(position["potentialQuantity"] - position["openQuantity"], 0) / 10) * 10
	print position["symbol"]
	print position["openQuantity"]
	print position["potentialQuantity"]
	print position["purchaseQuantity"]

ATTRIBUTES = ['currency', 'cash', 'marketValue', 'totalEquity']

def cad_balances_from_json(json):
    cad = next((cur for cur in json["perCurrencyBalances"] if cur["currency"] == "CAD"))
    return { k: v for k, v in cad.items() if k in ATTRIBUTES }

class ClientWrapper:
    def __init__(self, client):
        self.client = client

    def balances(self):
        return cad_balances_from_json(self.client.get_balances())

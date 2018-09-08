BALANCES_ATTRIBUTES = ['currency', 'cash', 'marketValue', 'totalEquity']
POSITIONS_ATTRIBUTES = ['currentPrice', 'openQuantity', 'currentMarketValue', 'averageEntryPrice']

def cad_balances_from_json(json, attributes=BALANCES_ATTRIBUTES):
    cad = next((cur for cur in json["perCurrencyBalances"] if cur["currency"] == "CAD"))
    return { k: v for k, v in cad.items() if k in attributes }

def positions_from_json(json, attributes=POSITIONS_ATTRIBUTES):
    positions = {}
    for p in json['positions']:
        symbol = p['symbol']
        position = { k: v for k, v in p.items() if k in attributes }
        positions[symbol] = position
    return positions

class ClientWrapper:
    def __init__(self, client):
        self.client = client

    def balances(self):
        return cad_balances_from_json(self.client.get_balances())

    def positions(self):
        return positions_from_json(self.client.get_positions())

    def symbol(self, symbol_request):
        return symbol_from_json(self.client.get_symbol(symbol_request))

    def quote(self, quote_request):
        return quote_from_json(self.client.get_quote(quote_request))

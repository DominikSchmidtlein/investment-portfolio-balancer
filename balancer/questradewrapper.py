from balancer import questrade
import balancer.configmanager as configuration

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
    def __init__(self, account_id, configmanager=None, client=None):
        if configmanager is None:
            configmanager = configuration.ConfigManager()
        config = configmanager.config()
        if client is None:
            client = questrade.Client(config['refresh_token'], account_id)
        config.update(client.login_response)
        configmanager.put_config(config)
        self.client = client

    def balances(self):
        return cad_balances_from_json(self.client.get_balances())

    def positions(self):
        return positions_from_json(self.client.get_positions())

    def last_trade_price(self, symbol):
        symbol_id = self.client.get_symbol(symbol)['symbols'][0]['symbolId']
        return self.client.get_quote(symbol_id)['quotes'][0]['lastTradePrice']

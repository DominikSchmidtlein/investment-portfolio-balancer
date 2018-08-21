from balancer.configmanager import ConfigManager
from balancer.questradeclient import QuestradeClient
from balancer.calculator import Calculator
from balancer.printer import Printer

COMPOSITION = {
    "VE.TO": { 'composition': 0.10 },
    "VA.TO": { 'composition': 0.10 },
    "VEE.TO": { 'composition': 0.10 },
    "VCN.TO": { 'composition': 0.20 },
    "VUN.TO": { 'composition': 0.30 },
    "BND.TO": { 'composition': 0.20 }
}
assert sum(v['composition'] for _, v in COMPOSITION.items()) == 1

def lambda_handler(event, context):
    # retrieve config
    configmanager = ConfigManager()
    config = configmanager.get_config()
    # connect to questrade
    qclient = QuestradeClient(config['refresh_token'], config['account_id'])
    # update config
    config.update(qclient.login_response)
    configmanager.put_config(config)
    # get portfolio positions
    positions = qclient.get_positions(False,
        ['currentPrice', 'openQuantity', 'symbolId', 'currentMarketValue', 'averageEntryPrice'])

    for symbol in set().union(positions.keys(), COMPOSITION.keys()):
        position = { 'composition': 0, **COMPOSITION.get(symbol, {}) }
        if symbol in positions:
            position.update(positions[symbol])
        else:
            position.update({ 'openQuantity': 0, 'currentMarketValue': 0, 'averageEntryPrice': 0 })
            symbol_id = qclient.get_symbol(symbol, ['symbolId'])['symbolId']
            current_price = qclient.get_quote(symbol_id, ['lastTradePrice'])['lastTradePrice']
            position.update({ 'symbolId': symbol_id, 'currentPrice': current_price })
        positions.update({ symbol: position })

    # get portfolio balances
    balances = qclient.get_balances(False, ['CAD'], ['currency', 'cash', 'marketValue', 'totalEquity'])[0]
    calculator = Calculator()
    purchases, new_balances = calculator.balance(positions, balances)

    # print portfolio
    printer = Printer()
    printer.print_transactions(purchases)
    printer.print_balances(new_balances)

if __name__ == '__main__':
    lambda_handler(None, None)

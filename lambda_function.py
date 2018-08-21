from balancer.configmanager import ConfigManager
from balancer.compositionmanager import CompositionManager
from balancer.questradeclient import QuestradeClient
from balancer.calculator import Calculator
from balancer.printer import Printer

def lambda_handler(event, context):
    # retrieve config
    configmanager = ConfigManager()
    config = configmanager.get_config()
    # connect to questrade
    qclient = QuestradeClient(config['refresh_token'], config['account_id'])
    # update config
    config.update(qclient.login_response)
    configmanager.put_config(config)
    # retrieve desired composition
    compositionmanager = CompositionManager()
    composition = compositionmanager.get_composition(int(config['account_id']))
    assert sum(v['composition'] for v in composition.values()) - 1 <= 0.00000001
    # get portfolio positions
    positions = qclient.get_positions(False,
        ['currentPrice', 'openQuantity', 'symbolId', 'currentMarketValue', 'averageEntryPrice'])

    for symbol in set().union(positions.keys(), composition.keys()):
        position = { 'composition': 0, **composition.get(symbol, {}) }
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

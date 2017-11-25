from configmanager import ConfigManager
from questradeclient import QuestradeClient
from calculator import Calculator
from printer import Printer

COMPOSITION = {
    "VE.TO": 0.23,
    "VA.TO": 0.15,
    "VEE.TO": 0.11,
    "VCN.TO": 0.04,
    "VUN.TO": 0.47
}
assert sum(COMPOSITION.itervalues()) == 1

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
        ['currentPrice', 'openQuantity', 'symbol', 'symbolId', 'currentMarketValue', 'averageEntryPrice'])
    for p in positions:
        p['composition'] = COMPOSITION.get(p['symbol'], 0)

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

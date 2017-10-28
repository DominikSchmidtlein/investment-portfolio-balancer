from configmanager import ConfigManager
from questradeclient import QuestradeClient
from calculator import Calculator
from printer import Printer

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
    positions = qclient.get_positions(False, ['currentPrice', 'openQuantity', 'symbol', 'symbolId', 'currentMarketValue'])
    # get portfolio balances
    balances = qclient.get_balances(False, ['CAD'], ['currency', 'cash', 'marketValue', 'totalEquity'])[0]
    calculator = Calculator()
    purchases = calculator.purchases(positions, balances)
    # print portfolio
    printer = Printer()
    printer.print_breakdown(calculator.calculate_percentages(positions))
    printer.print_transactions(purchases)
    printer.print_balances(balances, calculator.new_balances(balances, purchases))
    printer.print_breakdown(calculator.new_percentages(positions, purchases))

if __name__ == '__main__':
    lambda_handler(None, None)

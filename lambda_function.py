from configmanager import ConfigManager
from questradeclient import QuestradeClient
from calculator import Calculator

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
    balances = qclient.get_balances(False, ['CAD'], ['currency', 'cash', 'marketValue', 'totalEquity'])
    calculator = Calculator()
    purchases = calculator.purchases(positions, balances[0])

if __name__ == '__main__':
    lambda_handler(None, None)

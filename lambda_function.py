from configmanager import ConfigManager
from questradeclient import QuestradeClient

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
    positions = qclient.get_positions(False, ['currentPrice', 'openQuantity', 'symbol', 'symbolId'])
    # get portfolio balances
    balances = qclient.get_balances(False, ['CAD'], ['currency', 'cash', 'marketValue', 'totalEquity'])

if __name__ == '__main__':
    lambda_handler(None, None)

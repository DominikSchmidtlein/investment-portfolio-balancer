from balancer.configmanager import ConfigManager
from balancer import composition
from balancer import questrade
from balancer import calculator
from balancer.tablegenerator import TableGenerator
from balancer import email

def lambda_handler(event, context):
    # retrieve config
    configmanager = ConfigManager()
    config = configmanager.get_config()
    # connect to questrade
    qclient = questrade.Client(config['refresh_token'], config['account_id'])
    # update config
    config.update(qclient.login_response)
    configmanager.put_config(config)
    # retrieve desired composition
    comp = composition.retrieve(int(config['account_id']))
    assert sum(v['composition'] for v in comp.values()) - 1 <= 0.00000001
    # get portfolio positions
    positions = qclient.get_positions(
        ['currentPrice', 'openQuantity', 'symbolId', 'currentMarketValue', 'averageEntryPrice'])
    # get portfolio balances
    balances = qclient.get_balances(attributes=['currency', 'cash', 'marketValue', 'totalEquity'])
    # calculate balanced portfolio
    purchases, new_balances = calculator.balance(positions, balances, comp)
    # generate tables
    tablegenerator = TableGenerator()
    p_table = tablegenerator.transactions_table(purchases)
    b_table = tablegenerator.balances_table(new_balances)

    # email tables
    email.send_email("Questrade Portfolio Overview", str(p_table) + "\n\n" + str(b_table))

    # print tables
    print(p_table)
    print(b_table)

if __name__ == '__main__':
    lambda_handler(None, None)

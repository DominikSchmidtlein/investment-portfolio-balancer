from balancer.configmanager import ConfigManager
from balancer import composition
from balancer.questradeclient import QuestradeClient
from balancer import calculator
from balancer.tablegenerator import TableGenerator
from balancer import email

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
    comp = composition.retrieve(int(config['account_id']))
    assert sum(v['composition'] for v in comp.values()) - 1 <= 0.00000001
    # get portfolio positions
    positions = qclient.get_positions(False,
        ['currentPrice', 'openQuantity', 'symbolId', 'currentMarketValue', 'averageEntryPrice'])

    for symbol in set().union(positions.keys(), comp.keys()):
        position = { 'composition': 0, **comp.get(symbol, {}) }
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
    purchases, new_balances = calculator.balance(positions, balances)

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

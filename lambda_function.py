import settings
import os
from balancer import composition
from balancer import questradewrapper
from balancer import calculator
from balancer.tablegenerator import TableGenerator
from balancer import email
from balancer import portfoliodb

def lambda_handler(event, context):
    account_id = os.getenv("ACCOUNT_ID")
    print(account_id)
    # connect to questrade
    wrapper = questradewrapper.ClientWrapper(account_id)
    # retrieve desired composition
    comp = composition.retrieve(account_id)
    # get portfolio positions
    positions = wrapper.positions()
    # get portfolio balances
    balances = wrapper.balances()
    # calculate balanced portfolio
    new_positions, new_balances = calculator.balance(positions, balances, comp, price_getter(wrapper))
    # store calculations in db
    portfoliodb.save(account_id, new_balances, new_positions)
    # generate tables
    tablegenerator = TableGenerator()
    p_table = tablegenerator.transactions_table(new_positions)
    b_table = tablegenerator.balances_table(new_balances)

    # email tables
    email.send_email("Questrade Portfolio Overview 0.1", str(p_table) + "\n\n" + str(b_table))

    # print tables
    print(p_table)
    print(b_table)

def price_getter(client):
    def get_price(symbol):
        current_price = client.last_trade_price(symbol)
    return get_price

if __name__ == '__main__':
    lambda_handler(None, None)

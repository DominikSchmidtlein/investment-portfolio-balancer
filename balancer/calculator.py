import copy
from decimal import Decimal

def balance(positions, balances, composition, get_price=None, min_quantity=10):
    """balance(dict1, dict2) -> list, dict

    dict1 has nested dict with keys:
    'composition', 'currentPrice', 'currentMarketValue', 'openQuantity'
    dict2 has keys: 'totalEquity', 'cash', 'marketValue'

    Return a copy of dict with new nested keys:
    'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity'
    'before actual %', 'after actual %', 'ideal %'
    Return a copy of dict with keys 'newCash', 'newMarketValue'
    """
    positions = copy.deepcopy(positions)
    balances = copy.deepcopy(balances)
    composition = copy.deepcopy(composition)

    normalize_symbols(positions, composition, get_price)

    # calculate purchases
    balances['newCash'] = balances['cash']
    balances['newMarketValue'] = balances['marketValue']

    for s, p in positions.items():
        p['purchaseValue'] = Decimal(0)
        p['purchaseQuantity'] = Decimal(0)
        p['newMarketValue'] = p['currentMarketValue']
        p['newQuantity'] = p['openQuantity']
        p['allocation'] = balances['totalEquity'] * p['composition']

    # purchasable positions
    p_p = positions.copy()
    while p_p:
        # retrieve the position that is furthest from the desired allocation
        symbol = max(p_p, key=lambda x: p_p[x]['allocation'] - p_p[x]['newMarketValue'])
        p = p_p[symbol]
        cost = p['currentPrice'] * min_quantity
        needed = p['allocation'] >= p['newMarketValue'] + cost
        if needed and cost <= balances['newCash']:
            p['purchaseQuantity'] += min_quantity
            p['purchaseValue'] += cost
            p['newQuantity'] += min_quantity
            p['newMarketValue'] += cost
            balances['newCash'] -= cost
            balances['newMarketValue'] += cost
        else:
            del p_p[symbol]
    percentages(positions, balances['totalEquity'])

    return positions, balances

def normalize_symbols(positions, composition, get_price):
    for symbol in set().union(positions.keys(), composition.keys()):
        position = { 'composition': Decimal(0), **composition.get(symbol, {}) }
        if symbol in positions:
            position.update(positions[symbol])
        else:
            position.update({ 'openQuantity': Decimal(0), 'currentMarketValue': Decimal(0) })
            position['currentPrice'] = get_price(symbol)
        positions.update({ symbol: position })


def percentages(positions, total_equity):
    """percentages(dict) -> dict

    dict has nested dicts with keys: 'currentMarketValue', 'newMarketValue', 'composition'

    Return a copy of dict with new keys added to each nested dict:
    'before actual %', 'after actual %', 'ideal %'
    """

    for s, p in positions.items():
        p['before actual %'] = 100 * p['currentMarketValue'] / total_equity
        p['after actual %'] = 100 * p['newMarketValue'] / total_equity
        p['ideal %'] = p['composition'] * 100

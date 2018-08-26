def balance(positions, balances, min_quantity=10):
    """balance(dict1, dict2) -> list, dict

    dict1 has nested dict with keys:
    'composition', 'currentPrice', 'currentMarketValue', 'openQuantity'
    dict2 has keys: 'totalEquity', 'cash', 'marketValue'

    Return a copy of dict with new nested keys:
    'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity'
    'before actual %', 'after actual %', 'ideal %'
    Return a copy of dict with keys 'newCash', 'newMarketValue'
    """

    # calculate purchases
    new_balances = balances.copy()
    new_balances['newCash'] = balances['cash']
    new_balances['newMarketValue'] = balances['marketValue']

    purchases = {}
    for s, p in positions.items():
        n_p = p.copy()
        n_p['purchaseValue'] = 0
        n_p['purchaseQuantity'] = 0
        n_p['newMarketValue'] = p['currentMarketValue']
        n_p['newQuantity'] = p['openQuantity']
        n_p['allocation'] = balances['totalEquity'] * p['composition']
        purchases[s] = n_p

    # purchasable positions
    p_p = purchases.copy()
    while p_p:
        # retrieve the position that is furthest from the desired allocation
        symbol = max(p_p, key=lambda x: p_p[x]['allocation'] - p_p[x]['newMarketValue'])
        p = p_p[symbol]
        cost = p['currentPrice'] * min_quantity
        needed = p['allocation'] >= p['newMarketValue'] + cost
        if needed and cost <= new_balances['newCash']:
            p['purchaseQuantity'] += min_quantity
            p['purchaseValue'] += cost
            p['newQuantity'] += min_quantity
            p['newMarketValue'] += cost
            new_balances['newCash'] -= cost
            new_balances['newMarketValue'] += cost
        else:
            del p_p[symbol]
    return percentages(purchases, balances['totalEquity']), new_balances

def percentages(positions, total_equity):
    """percentages(dict) -> dict

    dict has nested dicts with keys: 'currentMarketValue', 'newMarketValue', 'composition'

    Return a copy of dict with new keys added to each nested dict:
    'before actual %', 'after actual %', 'ideal %'
    """

    w_percent = {}
    for s, p in positions.items():
        w_p = p.copy()
        w_p['before actual %'] = 100.0 * p['currentMarketValue'] / total_equity
        w_p['after actual %'] = 100.0 * p['newMarketValue'] / total_equity
        w_p['ideal %'] = p['composition'] * 100
        w_percent[s] = w_p
    return w_percent

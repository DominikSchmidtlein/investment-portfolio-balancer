class Calculator:
    def balance(self, positions, balances, min_quantity=10):
        """balance(list, dict) -> list, dict

        list has dict with keys:
        'composition', 'currentPrice', 'currentMarketValue', 'openQuantity'
        dict has keys: 'totalEquity', 'cash', 'marketValue'

        Return a copy of list with new keys:
        'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity'
        'before actual %', 'after actual %', 'ideal %'
        Return a copy of dict with keys 'newCash', 'newMarketValue'
        """

        # import pdb; pdb.set_trace()

        # calculate purchases
        new_balances = balances.copy()
        new_balances['newCash'] = balances['cash']
        new_balances['newMarketValue'] = balances['marketValue']

        purchases = []
        for p in positions:
            n_p = p.copy()
            n_p['purchaseValue'] = 0
            n_p['purchaseQuantity'] = 0
            n_p['newMarketValue'] = p['currentMarketValue']
            n_p['newQuantity'] = p['openQuantity']
            # theoretical market value
            n_p['tMV'] = balances['totalEquity'] * p['composition']
            purchases.append(n_p)

        # purchasable positions
        p_p = purchases[:]
        while p_p:
            p = max(p_p, key=lambda x: x['tMV'] - x['newMarketValue'])
            cost = p['currentPrice'] * min_quantity
            needed = p['tMV'] >= p['newMarketValue'] + cost
            if needed and cost <= new_balances['newCash']:
                p['purchaseQuantity'] += min_quantity
                p['purchaseValue'] += cost
                p['newQuantity'] += min_quantity
                p['newMarketValue'] += cost
                new_balances['newCash'] -= cost
                new_balances['newMarketValue'] += cost
            else:
                del p['tMV']
                p_p.remove(p)
        return self._percentages(purchases, balances['totalEquity']), new_balances

    def _percentages(self, positions, total_equity):
        """percentages(list) -> list

        list has dicts with keys: 'currentMarketValue', 'newMarketValue', 'composition'

        Return a copy of list with new keys added to each dict:
        'before actual %', 'after actual %', 'ideal %'
        """

        w_percent = []
        for p in positions:
            w_p = p.copy()
            w_p['before actual %'] = 100.0 * p['currentMarketValue'] / total_equity
            w_p['after actual %'] = 100.0 * p['newMarketValue'] / total_equity
            w_p['ideal %'] = p['composition'] * 100
            w_percent.append(w_p)
        return w_percent

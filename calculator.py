class Calculator:
    def balance(self, positions, balances):
        """balance(list, dict) -> list, dict

        list has dict with keys: 'composition', 'currentPrice', 'currentMarketValue'
        dict has keys: 'totalEquity', 'cash', 'marketValue'

        Return a copy of list with new keys:
        'purchaseValue', 'purchaseQuantity', 'newMarketValue',
        'before actual %', 'after actual %', 'ideal %'
        Return a copy of dict with keys 'newCash', 'newMarketValue'
        """
        # calculate purchases
        purchases = self._purchases(positions, balances)
        # calculate post purchase balances
        new_balances = self._new_balances(balances, purchases)
        # compute percentages
        self._percentages(purchases)
        return purchases, new_balances

    def _percentages(self, positions):
        """percentages(list) -> list

        list has dicts with keys: 'currentMarketValue', 'newMarketValue', 'composition'

        Return a copy of list with new keys added to each dict:
        'before actual %', 'after actual %', 'ideal %' and new entry 'Total'
        """

        c_total_value = float(sum(p['currentMarketValue'] for p in positions))
        n_total_value = float(sum(p['newMarketValue'] for p in positions))

        w_percent = []
        for p in positions:
            w_p = p.copy()
            w_p['before actual %'] = p['currentMarketValue'] / c_total_value * 100
            w_p['after actual %'] = p['newMarketValue'] / n_total_value * 100
            w_p['ideal %'] = p['composition'] * 100
            w_percent.append(w_p)
        w_percent.append({
            'symbol': 'Total',
            'currentMarketValue': c_total_value,
            'newMarketValue': n_total_value,
            'before actual %': sum(p['before actual %'] for p in w_percent),
            'after actual %': sum(p['after actual %'] for p in w_percent),
            'ideal %': sum(p['ideal %'] for p in w_percent)
        })
        return w_percent

    def _new_balances(self, balances, purchases):
        """new_balances(dict, list) -> dict

        dict has keys: 'cash', 'marketValue'
        list has dict with key 'purchaseValue'

        Return copy of dict with new keys: 'newCash', 'newMarketValue'
        """
        total_purchases = sum(p['purchaseValue'] for p in purchases)
        # python3.6 {**balances, **{...}}
        new_balances = balances.copy()
        new_balances['newCash'] = balances['cash'] - total_purchases
        new_balances['newMarketValue'] = balances['marketValue'] + total_purchases
        return new_balances

    def _purchases(self, positions, balances):
        """purchases(list, dict) -> list

        list must have dict with keys: 'composition', 'currentPrice', 'currentMarketValue'
        dict must have keys: 'totalEquity', 'cash'

        Return a copy of list with new keys: 'purchaseValue', 'purchaseQuantity', 'newMarketValue'
        """
        # which securities are needed
        n_positions = []
        composition_total = 0
        normalized_equity = balances['cash']
        for p in positions:
            p = p.copy()
            if p['currentMarketValue'] >= balances['totalEquity'] * p['composition']:
                p['n_composition'] = 0
            else:
                p['n_composition'] = p['composition']
                composition_total += p['n_composition']
                normalized_equity += p['currentMarketValue']
            n_positions.append(p)

        for p in n_positions:
            # normalized composition
            p['n_composition'] /= composition_total
            # theoretical market value
            t_mv = normalized_equity * p['n_composition']
            # theoretical purchase value
            t_pv = max(t_mv - p['currentMarketValue'], 0)
            # theoretical purchase quantity
            t_pq = t_pv / p['currentPrice']
            # practical purchase quantity
            p['purchaseQuantity'] = int(t_pq // 10 * 10)
            # practical purchase value
            p['purchaseValue'] = p['purchaseQuantity'] * p['currentPrice']
            # new market value
            p['newMarketValue'] = p['currentMarketValue'] + p['purchaseValue']
            del p['n_composition']
        return n_positions

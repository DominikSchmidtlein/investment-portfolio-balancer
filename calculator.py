class Calculator:
    def __init__(self, composition=None):
        self.composition = composition if composition else {
          "VE.TO": 0.23,
          "VA.TO": 0.15,
          "VEE.TO": 0.11,
          "VCN.TO": 0.04,
          "VUN.TO": 0.47
        }
        assert sum(self.composition.itervalues()) == 1

    def calculate_percentages(self, positions):
        total_market_value = sum(p['currentMarketValue'] for p in positions)
        positions_w_percentages = [{
            'symbol': p['symbol'],
            'marketValue': p['currentMarketValue'],
            'actual %': p['currentMarketValue'] / total_market_value * 100,
            'ideal %': self.composition[p['symbol']] * 100
        } for p in positions]
        positions_w_percentages.append({
            'symbol': 'Total',
            'marketValue': total_market_value,
            'actual %': sum(p['actual %'] for p in positions_w_percentages),
            'ideal %': sum(p['ideal %'] for p in positions_w_percentages)
        })
        return positions_w_percentages

    def new_percentages(self, positions, purchases):
        new_positions = [
            {
                'symbol': p['symbol'],
                'currentMarketValue': p['currentMarketValue'] +
                sum(x['purchaseValue'] for x in purchases if x['symbol'] == p['symbol'])
            } for p in positions
        ]
        return self.calculate_percentages(new_positions)

    def new_balances(self, old_balances, purchases):
        total_purchase_value = sum(p['purchaseValue'] for p in purchases)
        return {
            'cash': old_balances['cash'] - total_purchase_value,
            'marketValue': old_balances['marketValue'] + total_purchase_value,
            'totalEquity': old_balances['totalEquity']
        }

    def purchases(self, positions, balances):
        # which securities are needed
        needed_positions = filter(lambda position:
            position['currentMarketValue'] < balances['totalEquity'] * self.composition[position['symbol']],
            positions)
        # calculate new composition
        normalized_composition = self.__new_composition(needed_positions)
        # how much equity do we have to work with
        normalized_equity = sum(p['currentMarketValue'] for p in needed_positions) + balances['cash']
        # what should we purchase
        return map(lambda position: self.__needed_purchase_quantity(position, normalized_equity, normalized_composition),
            needed_positions)

    def __new_composition(self, needed_positions):
        needed_compositions = { p['symbol']: self.composition[p['symbol']] for p in needed_positions }
        composition_total = sum(needed_compositions.itervalues())
        normalized_composition = { k: v / composition_total for k, v in needed_compositions.items() }
        assert int(sum(normalized_composition.itervalues())) == 1
        return normalized_composition

    def __needed_purchase_quantity(self, position, total_equity, composition):
        theoretical_market_value = total_equity * composition[position['symbol']]
        theoretical_purchase_value = max(theoretical_market_value - position['currentMarketValue'], 0)
        assert theoretical_purchase_value > 0
        theoretical_purchase_quantity = theoretical_purchase_value / position['currentPrice']
        practical_purchase_quantity = int(theoretical_purchase_quantity // 10 * 10)
        practical_purchase_value = practical_purchase_quantity * position['currentPrice']
        return {
            'symbol': position['symbol'],
            'symbolId': position['symbolId'],
            'currentPrice': position['currentPrice'],
            'averageEntryPrice': position['averageEntryPrice'],
            'purchaseValue': practical_purchase_value,
            'purchaseQuantity': practical_purchase_quantity
        }

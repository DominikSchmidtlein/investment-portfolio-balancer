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

    def purchases(self, positions, balances):
        # which securities are needed
        needed_positions = filter(lambda position:
            position['currentMarketValue'] < balances['totalEquity'] * self.composition[position['symbol']],
            positions)
        # calculate new composition
        normalized_composition = { p['symbol']: self.composition[p['symbol']] for p in needed_positions }
        composition_total = sum(normalized_composition.itervalues())
        normalized_composition = { k: v / composition_total for k, v in normalized_composition.items() }
        assert int(sum(normalized_composition.itervalues())) == 1
        # how much equity do we have to work with
        normalized_equity = sum(p['currentMarketValue'] for p in needed_positions) + balances['cash']
        # what should we purchase
        return map(lambda position: self.__needed_purchase_quantity(position, normalized_equity, normalized_composition),
            needed_positions)

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
            'purchaseValue': practical_purchase_value,
            'purchaseQuantity': practical_purchase_quantity
            }

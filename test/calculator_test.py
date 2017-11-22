from calculator import Calculator

import unittest

class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    # def test_balance(self):
    #     positions = [{'composition': 1, 'currentPrice': 1, 'currentMarketValue': 1}]
    #     balances = {'totalEquity': 1, 'marketValue': 1, 'cash': 1}
    #     purchases, new_balances = self.calculator.balance(positions, balances)

    def test_new_balances(self):
        balances = { 'cash': 5, 'marketValue': 5, 'totalEquity': 10 }
        purchases = [{ 'purchaseValue': 1 } for _ in xrange(4)]
        expected = { 'cash':    5, 'marketValue':    5, 'totalEquity': 10,
                     'newCash': 1, 'newMarketValue': 9 }
        result = self.calculator._new_balances(balances, purchases)
        self.assertEqual(expected, result)

    def test_percentages(self):
        position_values = [(.3, 6, 10, 60, 50, 30),
                           (.3, 2, 0, 20,  0, 30),
                           (.4, 2, 10, 20, 50, 40)]
        positions = []
        expected = []
        for a, b, c, d, e, f in position_values:
            x = { 'composition': a, 'currentMarketValue': b, 'newMarketValue': c }
            y = x.copy()
            y.update({ 'before actual %': d, 'after actual %': e, 'ideal %': f })
            positions.append(x)
            expected.append(y)
        expected.append({ 'symbol': 'Total', 'currentMarketValue': 10, 'newMarketValue': 20,
                          'before actual %': 100, 'after actual %': 100, 'ideal %': 100})
        result = self.calculator._percentages(positions)
        self.assertEqual(expected, result)

    def test_purchases_all_needed(self):
        positions = [{'composition': .3, 'currentPrice': 2, 'currentMarketValue': 150},
                     {'composition': .3, 'currentPrice': 1, 'currentMarketValue': 250},
                     {'composition': .4, 'currentPrice': 3, 'currentMarketValue': 250}]
        balances = { 'cash': 350, 'marketValue': 650, 'totalEquity': 1000 }
        expected_values = [(.3, 2, 150, 140, 70, 290),
                           (.3, 1, 250,  50, 50, 300),
                           (.4, 3, 250, 150, 50, 400)]
        expected = self._generate_purchases(expected_values)
        result = self.calculator._purchases(positions, balances)
        self.assertEqual(expected, result)

    def test_purchases_not_all_needed(self):
        positions = [{'composition': .3, 'currentPrice': 2, 'currentMarketValue': 500},
                     {'composition': .3, 'currentPrice': 1, 'currentMarketValue': 150},
                     {'composition': .4, 'currentPrice': 5, 'currentMarketValue': 0}]
        balances = { 'cash': 350, 'marketValue': 650, 'totalEquity': 1000 }
        # python3.6 => { **positions[0], **{'purchaseValue': 0} }
        expected_values = [(.3, 2, 500,   0,  0, 500),
                           (.3, 1, 150,  60, 60, 210),
                           (.4, 5,   0, 250, 50, 250)]
        expected = self._generate_purchases(expected_values)
        result = self.calculator._purchases(positions, balances)
        self.assertEqual(expected, result)

    def _generate_purchases(self, expected_values):
        return map(lambda (a, b, c, d, e, f): {
            'composition': a,
            'currentPrice': b,
            'currentMarketValue': c,
            'purchaseValue': d,
            'purchaseQuantity': e,
            'newMarketValue': f
        }, expected_values)

if __name__ == '__main__':
    unittest.main()

# python -m test.calculator_test

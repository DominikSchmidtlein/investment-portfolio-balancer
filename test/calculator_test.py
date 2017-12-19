from calculator import Calculator
import unittest

class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_balance(self):
        position_keys = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity')
        position_values = ((.2, 1, 100, 100), (.3, 2, 200, 100), (.5, .5, 50, 100))
        positions = self._generate_list_of_dict(position_keys, position_values)
        balances = { 'totalEquity': 1000, 'marketValue': 350, 'cash': 650 }
        # expected purchases keys
        expected_p_k = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity',
                        'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity',
                        'before actual %', 'after actual %', 'ideal %')
        # expected purchases values
        expected_p_v = ((.2,  1, 100, 100, 100, 100, 200, 200, 10, 20, 20),
                        (.3,  2, 200, 100, 100,  50, 300, 150, 20, 30, 30),
                        (.5, .5,  50, 100, 450, 900, 500,1000,  5, 50, 50))
        # expected purchases
        expected_p = self._generate_list_of_dict(expected_p_k, expected_p_v)

        expected_balances = balances.copy()
        expected_balances.update({ 'newCash': 0, 'newMarketValue': 1000 })

        purchases, new_balances = self.calculator.balance(positions, balances)

        self.assertEqual(expected_p, purchases)
        self.assertEqual(expected_balances, new_balances)

    def test_new_balances(self):
        balances = { 'cash': 5, 'marketValue': 5, 'totalEquity': 10 }
        purchases = [{ 'purchaseValue': 1 } for _ in range(4)]
        # python3.6 { **balances, **{ 'newCash': 1, 'newMarketValue': 9 } }
        expected = { 'cash':    5, 'marketValue':    5, 'totalEquity': 10,
                     'newCash': 1, 'newMarketValue': 9 }
        result = self.calculator._new_balances(balances, purchases)
        self.assertEqual(expected, result)

    def test_percentages(self):
        total_equity = 20
        position_values = ((.3, 6, 10, 30, 50, 30),
                           (.3, 2,  0, 10,  0, 30),
                           (.4, 2, 10, 10, 50, 40))
        positions = []
        expected = []
        for a, b, c, d, e, f in position_values:
            x = { 'composition': a, 'currentMarketValue': b, 'newMarketValue': c }
            # python3.6 { **x, **{} }
            y = x.copy()
            y.update({ 'before actual %': d, 'after actual %': e, 'ideal %': f })
            positions.append(x)
            expected.append(y)
        result = self.calculator._percentages(positions, total_equity)
        self.assertEqual(expected, result)

    def test_purchases_all_needed(self):
        positions = [{'composition': .3, 'currentPrice': 2, 'currentMarketValue': 150, 'openQuantity':  75},
                     {'composition': .3, 'currentPrice': 1, 'currentMarketValue': 250, 'openQuantity': 250},
                     {'composition': .4, 'currentPrice': 5, 'currentMarketValue': 250, 'openQuantity':  50}]
        balances = { 'cash': 350, 'marketValue': 650, 'totalEquity': 1000 }
        expected_keys = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity',
                         'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity')
        expected_values = ((.3, 2, 150,  75, 140, 70, 290, 145),
                           (.3, 1, 250, 250,  50, 50, 300, 300),
                           (.4, 5, 250,  50, 150, 30, 400, 80))
        expected = self._generate_list_of_dict(expected_keys, expected_values)
        result = self.calculator._purchases(positions, balances)
        self.assertEqual(expected, result)

    def test_purchases_not_all_needed(self):
        positions = [{'composition': .3, 'currentPrice': 2, 'currentMarketValue': 500, 'openQuantity': 250},
                     {'composition': .3, 'currentPrice': 1, 'currentMarketValue': 150, 'openQuantity': 150},
                     {'composition': .4, 'currentPrice': 5, 'currentMarketValue':   0, 'openQuantity':   0}]
        balances = { 'cash': 350, 'marketValue': 650, 'totalEquity': 1000 }

        # python3.6 => { **positions[0], **{'purchaseValue': 0} }
        expected_keys = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity',
                         'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity')
        expected_values = [(.3, 2, 500, 250,   0,  0, 500, 250),
                           (.3, 1, 150, 150,  60, 60, 210, 210),
                           (.4, 5,   0,   0, 250, 50, 250,  50)]
        expected = self._generate_list_of_dict(expected_keys, expected_values)
        result = self.calculator._purchases(positions, balances)
        self.assertEqual(expected, result)

    def _generate_list_of_dict(self, keys, values):
        return [{ key: entry[i] for i, key in enumerate(keys) } for entry in values]

if __name__ == '__main__':
    unittest.main()

# python -m test.calculator_test

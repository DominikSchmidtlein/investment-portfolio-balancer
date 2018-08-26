import unittest
from random import random, randint
from copy import deepcopy
import json
from balancer import calculator

class CalculatorTest(unittest.TestCase):
    DATA_PATH = 'test/testdata/calculator_test/'

    # python3.6 -m unittest test.calculator_test.CalculatorTest.test_balance_random_inputs
    def test_balance_random_inputs(self):
        positions, balances, composition = self._generate_random_inputs()

        positions_c = deepcopy(positions)
        balances_c = balances.copy()
        prices = {}

        def get_price(symbol):
            price = random() * 100.0
            prices[symbol] = price
            return price

        purchases, new_balances = calculator.balance(positions_c, balances_c, composition, get_price)

        # test inputs haven't been modified
        self.assertEqual(positions, positions_c)
        self.assertEqual(balances, balances_c)
        # test common values are consistent between input and output
        self.assertEqual(balances, { k: v for k, v in new_balances.items() if k in balances.keys() })
        for symbol, position in positions.items():
            self.assertEqual(position, { k: v for k, v in purchases[symbol].items() if k in position })
        for symbol, price in prices.items():
            self.assertEqual(price, purchases[symbol]['currentPrice'])

        self.assertAlmostEqual(1, sum((p['composition'] for p in purchases.values())))

        # test symbol no overlap in positions and prices symbols
        self.assertFalse(set(positions).intersection(set(prices)))
        # test purchases symbol sum of positions and prices
        self.assertEqual(set(purchases), set(positions).union(set(prices)))

        # test new_balances
        self.assertEqual(new_balances['totalEquity'], new_balances['marketValue'] + new_balances['cash'])
        self.assertAlmostEqual(new_balances['totalEquity'], new_balances['newMarketValue'] + new_balances['newCash'])
        self.assertTrue(new_balances['newMarketValue'] >= new_balances['marketValue'])

        # test on outputs only
        s_currentMarketValue = 0
        s_purchaseValue = 0
        s_newMarketValue = 0
        # test purchases
        for s, p in purchases.items():
            self.assertTrue(p['purchaseQuantity'] >= 0)
            self.assertAlmostEqual(p['currentMarketValue'], p['currentPrice'] * p['openQuantity'])
            self.assertAlmostEqual(p['purchaseValue'], p['currentPrice'] * p['purchaseQuantity'])
            self.assertAlmostEqual(p['newMarketValue'], p['currentPrice'] * p['newQuantity'])
            self.assertEqual(p['newQuantity'], p['openQuantity'] + p['purchaseQuantity'])
            self.assertAlmostEqual(p['newMarketValue'], p['currentMarketValue'] + p['purchaseValue'])
            self.assertTrue(p['newMarketValue'] >= p['currentMarketValue'])

            if p['allocation'] > p['currentMarketValue']:
                self.assertTrue(p['allocation'] >= p['newMarketValue'])
            else:
                self.assertEqual(0, p['purchaseValue'])

            s_currentMarketValue += p['currentMarketValue']
            s_purchaseValue += p['purchaseValue']
            s_newMarketValue += p['newMarketValue']

        # cross reference purchases and new_balances
        self.assertAlmostEqual(new_balances['marketValue'], s_currentMarketValue)
        self.assertAlmostEqual(new_balances['newMarketValue'], s_newMarketValue)
        self.assertAlmostEqual(s_newMarketValue, s_currentMarketValue + s_purchaseValue)
        self.assertAlmostEqual(new_balances['newCash'], new_balances['cash'] - s_purchaseValue)
        self.assertTrue(new_balances['cash'] >= s_purchaseValue)

    def _generate_random_inputs(self):
        # setup positions
        positions = {}
        balances = { 'marketValue': 0 }
        for n in range(randint(1,5)):
            price = random() * 100.0
            quantity = randint(0, 100)
            currentMarketValue = price * quantity
            balances['marketValue'] += currentMarketValue
            positions[str(n)] = {
                'currentPrice': price,
                'openQuantity': quantity,
                'currentMarketValue': currentMarketValue
            }
        balances['cash'] = randint(0, 2000)
        balances['totalEquity'] =  balances['cash'] + balances['marketValue']

        # get random number of random numbers
        rands = [random() for _ in range(randint(1,5))]
        tot = sum(rands)
        # setup composition
        composition = {}
        for n, r in enumerate(rands):
            composition[str(n)] = {
                'composition': r/tot
            }
        return positions, balances, composition

    def test_balance(self):
        self._test_balance(directory_path='test_balance/')

    def test_balance_all_needed(self):
        self._test_balance(directory_path='test_balance_all_needed/')

    def test_balance_not_all_needed(self):
        self._test_balance(directory_path='test_balance_not_all_needed/')

    def test_balance_different_symbols(self):
        self._test_balance(directory_path='test_balance_different_symbols/')

    def _test_balance(self,
                      directory_path,
                      inputs_directory='inputs/',
                      outputs_directory='outputs/',
                      positions_filename='positions.json',
                      balances_filename='balances.json',
                      composition_filename='composition.json',
                      prices_filename='prices.json',
                      purchases_filename='purchases.json',
                      new_balances_filename='new_balances.json'):

        input_dir_path = directory_path + inputs_directory
        output_dir_path = directory_path + outputs_directory

        positions = self._data(input_dir_path, positions_filename)
        balances = self._data(input_dir_path, balances_filename)
        composition = self._data(input_dir_path, composition_filename)

        def get_price(symbol):
            return self._data(input_dir_path, prices_filename)[symbol]

        purchases, new_balances = calculator.balance(positions, balances, composition, get_price)

        # expected purchases
        x_purchases = self._data(output_dir_path, purchases_filename)
        # expected balances
        x_balances = self._data(output_dir_path, new_balances_filename)

        self.assertEqual(x_purchases, purchases)
        self.assertEqual(x_balances, new_balances)

    def _data(self, directory, filename):
        with open(self.DATA_PATH + directory + filename) as f:
            return json.load(f)

if __name__ == '__main__':
    unittest.main()

# python3.6 -m test.calculator_test

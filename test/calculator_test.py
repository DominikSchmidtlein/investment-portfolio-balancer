import unittest
from random import random, randint
from copy import deepcopy
import json
from balancer.calculator import Calculator

class CalculatorTest(unittest.TestCase):
    DATA_PATH = 'test/testdata/calculator_test/'

    def setUp(self):
        self.calculator = Calculator()

    # python3.6 -m unittest test.calculator_test.CalculatorTest.test_balance_random_inputs
    def test_balance_random_inputs(self):
        positions, balances = self._generate_random_inputs()

        positions_c = deepcopy(positions)
        balances_c = balances.copy()

        purchases, new_balances = self.calculator.balance(positions_c, balances_c)

        # test inputs haven't been modified
        self.assertEqual(positions, positions_c)
        self.assertEqual(balances, balances_c)
        # test common values are consistent between input and output
        self.assertEqual(balances, { k: v for k, v in new_balances.items() if k in balances.keys() })
        self.assertEqual(positions, {s: {k: v for k, v in p.items() if k in next(iter(positions.values()))} for s, p in purchases.items()})

        self.assertAlmostEqual(1, sum((p['composition'] for _, p in purchases.items())))

        # test new_balances
        self.assertEqual(new_balances['totalEquity'], new_balances['marketValue'] + new_balances['cash'])
        self.assertAlmostEqual(new_balances['totalEquity'], new_balances['newMarketValue'] + new_balances['newCash'])
        self.assertTrue(new_balances['newMarketValue'] >= new_balances['marketValue'])

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
        # get random number of random numbers
        rands = [random() for _ in range(randint(1,5))]
        tot = sum(rands)

        positions = {}
        balances = { 'marketValue': 0 }
        for n, r in enumerate(rands):
            price = random() * 100.0
            quantity = randint(0, 100)
            currentMarketValue = price * quantity
            balances['marketValue'] += currentMarketValue
            positions[str(n)] = {
                'composition': r/tot,
                'currentPrice': price,
                'openQuantity': quantity,
                'currentMarketValue': currentMarketValue
            }
        balances['cash'] = randint(0, 2000)
        balances['totalEquity'] =  balances['cash'] + balances['marketValue']
        return positions, balances

    def test_balance(self):
        self._test_balance(directory_path='test_balance/')

    def test_balance_all_needed(self):
        self._test_balance(directory_path='test_balance_all_needed/')

    def test_balance_not_all_needed(self):
        self._test_balance(directory_path='test_balance_not_all_needed/')

    def _test_balance(self,
                      directory_path,
                      inputs_directory='inputs/',
                      outputs_directory='outputs/',
                      positions_filename='positions.json',
                      balances_filename='balances.json',
                      purchases_filename='purchases.json',
                      new_balances_filename='new_balances.json'):

        input_dir_path = directory_path + inputs_directory
        output_dir_path = directory_path + outputs_directory

        positions = self._data(input_dir_path, positions_filename)
        balances = self._data(input_dir_path, balances_filename)

        purchases, new_balances = self.calculator.balance(positions, balances)

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

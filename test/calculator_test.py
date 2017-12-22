import unittest
from random import random, randint
from copy import deepcopy
import json
from calculator import Calculator

class CalculatorTest(unittest.TestCase):
    DATA_PATH = 'test/testdata/calculator_test/'

    def setUp(self):
        self.calculator = Calculator()

    # python3.6 -m unittest test.calculator_test.CalculatorTest.test_balance_random_inputs
    def test_balance_random_inputs(self):
        rands = [random() for _ in range(randint(1,5))]
        tot = sum(rands)
        norm = [r / tot for r in rands]

        positions = []
        marketValue = 0
        for r in rands:
            price = random() * 100.0
            quantity = randint(0, 100)
            currentMarketValue = price * quantity
            marketValue += currentMarketValue
            positions.append({
                'composition': r/tot,
                'currentPrice': price,
                'openQuantity': quantity,
                'currentMarketValue': currentMarketValue
            })
        cash = randint(0, 2000)
        balances = { 'totalEquity': cash + marketValue, 'marketValue': marketValue, 'cash': cash }

        purchases, new_balances = self.calculator.balance(positions, balances.copy())

        try:
            # test that
            self.assertEqual(balances, { k: v for k, v in new_balances.items() if k in balances.keys() })
            self.assertEqual(positions, [{k:v for k,v in p.items() if k in positions[0].keys()} for p in purchases])

            self.assertAlmostEqual(1, sum((p['composition'] for p in positions)))
            self.assertTrue(new_balances['cash'] >= (sum(p['purchaseValue'] for p in purchases)))
        except AssertionError:
            print(json.dumps(purchases, indent=1))
            print(json.dumps(new_balances, indent=1))
            print(sum(p['purchaseValue'] for p in purchases))
            raise

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

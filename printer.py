from prettytable import PrettyTable

class Printer:
    def __init__(self):
        pass

    def print_transactions(self, transactions):
        columns = ['Symbol', 'Purchase Quantity', 'Purchase Value', 'Current Price', 'Average Entry Price']
        f = self._formatter(2)
        table = PrettyTable(columns)
        table.align.update({ c: 'r' for c in columns[1:] })
        for t in transactions:
            table.add_row([t['symbol'],
                           t['purchaseQuantity'],
                           f(t['purchaseValue']),
                           f(t['currentPrice']),
                           f(t['averageEntryPrice'])])
        print table

    def print_breakdown(self, positions):
        columns = ['Symbol', 'Market Value (CAD)', 'Actual %', 'Ideal %']
        f = self._formatter(2)
        table = PrettyTable(columns)
        table.align.update({ c: 'r' for c in columns[1:] })
        for p in positions:
            table.add_row([
                p['symbol'],
                f(p['marketValue']),
                f(p['actual %']),
                f(p['ideal %'])])
        print table

    def print_balances(self, balances):
        columns = ['Balance', 'Before', 'After']
        f = self._formatter(2)
        table = PrettyTable(columns)
        table.align.update({ c: 'r' for c in columns[1:] })
        table.add_row(['Cash',         f(balances['cash']),        f(balances['newCash'])])
        table.add_row(['Market Value', f(balances['marketValue']), f(balances['newMarketValue'])])
        table.add_row(['Total Equity', f(balances['totalEquity']), f(balances['totalEquity'])])
        print table

    def _formatter(self, decimals):
        def f(value):
            return "{0:.{1}f}".format(value, decimals)
        return f

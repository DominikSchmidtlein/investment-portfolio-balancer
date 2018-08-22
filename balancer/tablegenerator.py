from prettytable import PrettyTable

class TableGenerator:
    LEGEND = (
            'I%: Ideal %\n'
            'CP: Current Price\n'
            'AP: Average Price\n'
            'CQ: Current Quantity\n'
            'CMV: Current Market Value\n'
            'C%: Current %\n'
            'PQ: Purchase Quantity\n'
            'PV: Purchase Value\n'
            'NQ: New Quantity\n'
            'NMV: New Market Value\n'
            'N%: New %')

    def __init__(self):
        pass

    def transactions_table(self, transactions):
        columns = ['Symbol', 'I%', 'CP', 'AP', 'CQ', 'CMV', 'C%', 'PQ', 'PV', 'NQ', 'NMV', 'N%']
        table = PrettyTable(columns)
        table.align.update({ c: 'r' for c in columns[1:] })
        f = self._formatter(2)
        for s, t in transactions.items():
            table.add_row([s,
                           f(t['ideal %']),
                           f(t['currentPrice']),
                           f(t['averageEntryPrice']),
                           t['openQuantity'],
                           f(t['currentMarketValue']),
                           f(t['before actual %']),
                           t['purchaseQuantity'],
                           f(t['purchaseValue']),
                           f(t['newQuantity']),
                           f(t['newMarketValue']),
                           f(t['after actual %'])])
        return table

    def balances_table(self, balances):
        columns = ['Balance', 'Before', 'After']
        f = self._formatter(2)
        table = PrettyTable(columns)
        table.align.update({ c: 'r' for c in columns[1:] })
        table.add_row(['Cash',         f(balances['cash']),        f(balances['newCash'])])
        table.add_row(['Market Value', f(balances['marketValue']), f(balances['newMarketValue'])])
        table.add_row(['Total Equity', f(balances['totalEquity']), f(balances['totalEquity'])])
        return table

    def _formatter(self, decimals):
        def f(value):
            return "{0:.{1}f}".format(value, decimals)
        return f

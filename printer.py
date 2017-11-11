from prettytable import PrettyTable

class Printer:
    def __init__(self):
        pass

    def print_transactions(self, transactions):
        table = PrettyTable(['Symbol', 'Purchase Quantity', 'Purchase Value', 'Current Price', 'Average Entry Price'])
        table.align.update({'Purchase Quantity': 'r', 'Purchase Value': 'r', 'Current Price': 'r', 'Average Entry Price': 'r'})
        for t in transactions:
            table.add_row([t['symbol'], t['purchaseQuantity'], t['purchaseValue'], t['currentPrice'], t['averageEntryPrice']])
        print table

    def print_breakdown(self, positions):
        table = PrettyTable(['Symbol', 'Market Value (CAD)', 'Actual %', 'Ideal %'])
        table.align.update({'Market Value (CAD)': 'r', 'Actual %': 'r', 'Ideal %': 'r'})
        for p in positions:
            table.add_row([
                p['symbol'],
                round(p['marketValue'], 2),
                round(p['actual %'], 1),
                round(p['ideal %'], 1)])
        print table

    def print_balances(self, old_balances, new_balances):
        table = PrettyTable(['Balance', 'Before', 'After'])
        table.align.update({'Balance': 'l', 'Before': 'r', 'After': 'r'})
        table.add_row(['Cash', round(old_balances['cash'], 2), round(new_balances['cash'], 2)])
        table.add_row(['Market Value', round(old_balances['marketValue'], 2), round(new_balances['marketValue'], 2)])
        table.add_row(['Total Equity', round(old_balances['totalEquity'], 2), round(new_balances['totalEquity'], 2)])
        print table

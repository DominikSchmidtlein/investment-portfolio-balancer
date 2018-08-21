import boto3

class CompositionManager:
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table('InvestmentPortfolioBalancerComposition')

    def get_composition(self, account_id):
    	compositions = self.table.get_item(Key={'account_id': account_id})['Item']['compositions']
    	return { k1: { k2: float(v2) for k2, v2 in v1.items() } for k1, v1 in compositions.items() }

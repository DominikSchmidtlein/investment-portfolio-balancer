import boto3

class RefreshToken(object):
    """docstring for RefreshToken"""
    def __init__(self, account_id):
        super(RefreshToken, self).__init__()
        self.account_id = account_id
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table('InvestmentPortfolioBalancerRefreshToken')

    def get(self):
        return self.table.get_item(Key={'account_id': self.account_id})['Item']['refresh_token']

    def save(self, refresh_token):
        self.table.put_item(Item={'account_id': self.account_id, 'refresh_token': refresh_token})

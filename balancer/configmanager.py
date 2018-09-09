import boto3

class ConfigManager:
    def __init__(self):
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table('InvestmentPortfolioBalancerConfig')

    def config(self):
        return self.table.get_item(Key={'name':'default'})['Item']

    def put_config(self, config):
        self.table.put_item(Item=config)

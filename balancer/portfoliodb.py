import boto3
from datetime import datetime

def save(account_id, balances, positions):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Portfolios')
    table.put_item(Item={'account_id': account_id,
                         'timestamp': datetime.utcnow().isoformat(),
                         'balances': balances,
                         'positions': positions})

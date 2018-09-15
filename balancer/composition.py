import boto3
import functools

def retrieve(account_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('InvestmentPortfolioBalancerComposition')
    compositions = table.get_item(Key={'account_id': account_id})['Item']['compositions']
    compositions = { k1: { k2: float(v2) for k2, v2 in v1.items() } for k1, v1 in compositions.items() }
    assert sum(v['composition'] for v in compositions.values()) - 1 <= 0.00000001
    return compositions

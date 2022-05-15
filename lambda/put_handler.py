import os
import json
import boto3


def handler(event, context):
    ddb = boto3.client('dynamodb')

    item_key = event["queryStringParameters"]["itemKey"]
    item_name = event["queryStringParameters"]["name"]
    table_name = os.environ["TABLE"]

    response = ddb.put_item(
        TableName=table_name,
        Item={
            'itemKey': {'S': item_key},
            'name': {'S': item_name}
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response)
    }

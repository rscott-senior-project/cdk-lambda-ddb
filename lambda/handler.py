import os
import json
import boto3


def handler(event, context):
    ddb = boto3.client('dynamodb')

    target_name = event["queryStringParameters"]["itemKey"]
    table_name = os.environ["TABLE"]

    response = ddb.get_item(
        TableName=table_name,
        Key={
            'itemKey': {
                'S': target_name
            }
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response)
    }
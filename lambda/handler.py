import os
import json
import boto3


def handler(event, context):
    ddb = boto3.client('dynamodb')

    target_name = event["queryStringParameters"]["itemKey"]

    response = ddb.get_item(
        TableName="rsp-demo-table-dev",
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
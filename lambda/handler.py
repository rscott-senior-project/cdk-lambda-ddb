import os
import json
import boto3


def handler(event, context):
    ddb = boto3.client('dynamodb')

    response = ddb.get_item(
        TableName="rsp-demo-table-dev",
        Key={
            'itemKey': {
                'S': 'name'
            }
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response
    }
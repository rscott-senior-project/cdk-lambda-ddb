import os
import json
import boto3


def handler(event, context):
    ddb = boto3.client('dynamodb')

    print(event)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(event)
    }

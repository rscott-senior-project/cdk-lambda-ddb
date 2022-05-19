import os
import json

def handler(event, context):

    print(event)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(event)
    }

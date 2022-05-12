from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as _apigw,
    aws_dynamodb as _ddb,
    aws_iam as _iam
)
from constructs import Construct

class CdkDdbStreamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        table = _ddb.Table.from_table_arn(
            self, "ItemsTable",
            "arn:aws:dynamodb:us-east-1:170976071768:table/rsp-demo-table-dev"
        )

        ddb_role = _iam.Role(
            self,
            "ddb_lambda_role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        ddb_role.add_to_policy(_iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["arn:aws:dynamodb:us-east-1:170976071768:table/rsp-demo-table-dev"],
            actions=["dynamodb:GetItem"]
        ))

        get_lambda = _lambda.Function(
            self, 'get_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='handler.handler',
            role=ddb_role
        )

        get_handler_api = _apigw.LambdaRestApi(
            self, "handler-endpoint",
            handler=get_lambda
        )

        put_lambda = _lambda.Function(
            self, 'put_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='put_handler.handler',
        )

        put_handler_api = _apigw.LambdaRestApi(
            self, "put-handler-endpoint",
            handler=put_lambda
        )




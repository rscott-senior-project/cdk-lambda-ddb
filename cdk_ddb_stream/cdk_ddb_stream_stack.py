from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as _apigw,
    aws_dynamodb as _ddb,
    aws_iam as _iam,
    aws_kinesis as _kns
)
from aws_cdk.aws_lambda_event_sources import DynamoEventSource
from constructs import Construct

class CdkDdbStreamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = _ddb.Table(
            self, "stream-demo-table",
            partition_key=_ddb.Attribute(name="itemKey", type=_ddb.AttributeType.STRING),
            replication_regions=["us-east-2", "us-west-2"],
            kinesis_stream=_kns.Stream(self, "demo-stream")
        )

        ddb_read_role = _iam.Role(
            self,
            "ddb_read_lambda_role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        ddb_read_role.add_to_policy(_iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[table.table_arn],
            actions=["dynamodb:GetItem"]
        ))

        ddb_write_role = _iam.Role(
            self,
            "ddb_write_lambda_role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        ddb_write_role.add_to_policy(_iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[table.table_arn],
            actions=["dynamodb:PutItem", "dynamodb:UpdateItem"]
        ))

        ddb_admin_role = _iam.Role(
            self,
            "ddb_admin_lambda_role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        ddb_write_role.add_to_policy(_iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[table.table_arn],
            actions=["dynamodb:*"]
        ))

        get_lambda = _lambda.Function(
            self, 'get_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='handler.handler',
            role=ddb_read_role
        )

        get_lambda.add_environment("TABLE", table.table_name)

        get_handler_api = _apigw.LambdaRestApi(
            self, "handler-endpoint",
            handler=get_lambda
        )

        put_lambda = _lambda.Function(
            self, 'put_handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='put_handler.handler',
            role=ddb_write_role
        )

        put_lambda.add_environment("TABLE", table.table_name)

        put_handler_api = _apigw.LambdaRestApi(
            self, "put-handler-endpoint",
            handler=put_lambda
        )

        stream_lambda = _lambda.Function(
            self, "stream_handler",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='stream_handler.handler',
        )

        stream_lambda.add_event_source(
            DynamoEventSource(
                table,
                starting_position=_lambda.StartingPosition.LATEST,
                batch_size=1
            )
        )

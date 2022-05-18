AWS Developer Associate Content Series : DynamoDB Streams and Event Mapping with Lambda
=======================================================================================

Created by Rob Scott, last modified on May 18, 2022

This demonstration will use the AWS Cloud Development kit to provision a serverless application with DynamoDB and Lambda. The database will be configured with DynamoDB streams; these can be used as an event source for another Lambda. It's a common use-case for maintaining records across several data sources-- updates in one database will trigger another update process elsewhere.

This is the first demonstration using the Cloud Development Kit (CDK), a library meant for deploying infrastructure as code. It is compatible with multiple programming languages; this lab will use Python.

Using the Cloud Development Kit
-------------------------------

The CDK is extremely powerful for provisioning resources quickly and in an organized manner. It is easier to understand than a YAML-based CloudFormation template, and much faster to write code for an application. Outputs from the CDK are called Stacks. This stack will host Lambda’s, DynamoDB, and a Kinesis Data Stream that captures the DynamoDB events.

Use `npm install -g aws-cdk` to install the CDK. Once installed, make a new directory with the desired name of you application. Enter `cdk init app --language python` on the command line and start the Stack procurement process. Once the set-up code is written, most of the work will be done in the directory that shares the name with your present working directory. It will be `<APP_NAME>_stack.py`.

Adding Infrastructure
---------------------

Import all of the dependencies necessary to declare the stack:

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

Add this code within the `__init__` of the Stack object:

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

This is a lot of code, so let's break down exactly what this Stack will spin up.

#### Lambda

*   3 Lambdas: `get_lambda`, `put_lambda`, `stream_lambda`
    
*   Runtime for all 3 are Python 3.7
    
*   The handler logic is being marked for reference in the constructor arguments
    
    *   `code`: The directory where the constructor can find the handler logic
        
    *   `handler`: The actual name of the function that will act as the Lambda handler (`<FILENAME.<HANDLER>`)
        

Using`stream_lambda` as an example, the `code` and `handler` constructor arguments are saying that the function can be found along the path `lambda/stream_handler`, and there is a function named `handler` in it.

*   **\[Line 61\]** Add an environment variable to each Lambda runtime with the name of the DynamoDB table, its a required argument for requests through the client
    

#### API Gateway endpoints

*   **\[Line 63\]** `get_lambda`, and `put_lambda` need API Gateway endpoints so that users can invoke them with REST requests
    
*   Their `handler` constructor argument should be the Lambda object created earlier in the script
    

#### IAM Roles

*   **\[Line 20\]** These are called _execution roles_
    
*   **\[Line 26\]** Provide any necessary permissions for the Lambda to do its job-- permissions for DynamoDB read/write need to be granted to the Lambda execution role
    
*   These roles are instantiated and then used for the `role` constructor argument for the Lambda object
    

#### DynamoDB

*   DynamoDB table with a specified `partition_key` in the constructor
    
*   **\[Line 5\]** Enable Streams by attaching a Kinesis Data Stream in the constructor arguments
    
*   This allows the code to use DynamoDB as an event source, per the last section of the code
    
*   **\[Line 75\]** The Stream can be an event mapping now and will invoke `stream_lambda` when the buffer has at least 1 event in the stream (`batch_size=1)`
    

Adding Handler Logic
--------------------

In the root directory of the app, make a directory called `lambda`, and copy the code over from the GitHub repository linked at the top of this page.

#### Boto3

The handler logic is fairly simple, but the one noteworthy component of these functions is the use of Boto3. This is the Python library for interfacing with AWS resources-- just as the AWS SDK is the library for JavaScript. Boto3 makes it very easy to make calls to DynamoDB and its [very well documented](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html).

#### Accessing environment variables

As it shows in the code, the Lambda environment variables that we added can be accessed through the `os` library.

os.environ\[<VAR_NAME>\]

Postman for API Interaction
---------------------------

Postman proved to be significantly more efficient for interacting with the API’s. To make sure that the Lambda’s are operating properly and in sync with DynamoDB, the API’s need to be invoked a few times and verified within the console that the items are persisting. Postman makes it _very_ fast to craft up REST requests with well-constructed parameters that the Lambda will act on. Learn how to utilize it [here](https://www.bing.com/ck/a?!&&p=81ebea344dc356daee7354407d2894540e47b1363eff07d6bb3cfa4e25390b1dJmltdHM9MTY1MjY2MjQwNiZpZ3VpZD01NzNhNjgxZC01NDZkLTRmZmYtYmEzNy0yYTVlMDM2YWZmMGMmaW5zaWQ9NTE3MA&ptn=3&fclid=97c43514-d4b2-11ec-bfa5-3299a6c53ce0&u=a1aHR0cHM6Ly93d3cucG9zdG1hbi5jb20v&ntb=1).

Kinesis Data Streams
--------------------

AWS Kinesis is a service meant for ingesting data records in real time. Kinesis has producers and consumers-- the services that write records to the stream, and those that read those records out of the stream. In this case, DynamoDB is writing events to a data stream while Lambda is being invoked once the buffer reaches a certain size. The event records are available to the Lambda as the `event` variable in the handler.

#### Stream Record Types

DynamoDB will ask to specify what kind of record should be written to the stream when any edits happen. It is called the `StreamViewType` and there are 4 types.

1.  `KEYS_ONLY`: Key of the updated item is written to the stream
    
2.  `NEW_IMAGE`: The entire item, as it appears now, is written to the stream
    
3.  `OLD_IMAGE`: The entire item, before the edits were made, is added to the stream
    
4.  `NEW_AND_OLD_IMAGES`: Both new and old versions of the item are added the stream
    

Deploy the Stack
----------------

Use `cdk deploy` to provision the resources-- this may take a few minutes. At the end of the deployment, the CDK should output two URL’s. One is to add items to the database and the other is to retrieve individual items from the DynamoDB based on a partition key. The `GET` URL is mainly to verify that items are being added to the database-- this can also be confirmed by navigating to the AWS console and observing the table contents.

#### Using Postman

Open Postman in the browser with a free account. Enter the URL for `put_lambda` in the URL box and change the request type to `POST`. There are two necessary fields to include on the request parameters:

*   `itemKey`: This is the partition key for the table; requests will not be successful without a string argument for this field.
    
*   `name`: This is a field that is referenced by multiple Lambda handlers, so it is important to make sure all DynamoDB objects have it.
    

Send the request and verify that the response does not report any errors.

In the DynamoDB console, check to see if any items have been successfully written to the database. The items that have been successfully written will be added to the Kinesis Stream, thus, invoking the Lambda. To check that the Lambda is being invoked properly, navigate to the Lambda console and click on the _Monitor_ tab. Select _View CloudWatch Logs_ and look at the most recent log group. There should be a printout of the `event`, just as the `stream_handler` logic does. Now we can see exactly what information is written to the stream.

Clean Up
--------

Use `cdk destroy` to delete all of the stack’s resources.

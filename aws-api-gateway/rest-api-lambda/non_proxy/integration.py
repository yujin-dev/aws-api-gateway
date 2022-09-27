import pulumi
import pulumi_aws as aws
import json
import boto3
import os

from requests import request

def create_lambda_function():
    fn_name="lambda-non-proxy-integration"
    account = boto3.client('sts').get_caller_identity()["Account"]

    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "logs:CreateLogGroup",
                    "Resource": f"arn:aws:logs:us-east-1:{account}:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": [
                        f"arn:aws:logs:us-east-1:{account}:log-group:/aws/lambda/{fn_name}:*"
                    ]
                }
            ]
        }
    )
    
    # 위의 policy를 포함한 role을 생성하여 lambda에 위임하도록 함 
    role = aws.iam.Role(
        "lambda-execution-role",
        assume_role_policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    }
                ],
            }
        ),
        inline_policies=[aws.iam.RoleInlinePolicyArgs(
            name=fn_name+"-inline-policy",
            policy = policy
        )],
        name=fn_name+"-role",
        description="Lambda execution role with logging permitted",
    )
    function = aws.lambda_.Function("lambda-function",
        name=fn_name,
        code=pulumi.FileArchive(os.path.join(os.path.dirname(__file__), "sample.zip")),
        role=role.arn,
        handler="index.handler",
        runtime="nodejs12.x",
        timeout=120,
    )

    # API Gateway에서 lambda function을 실행할 수 있도록 permisson 추가
    aws.lambda_.Permission("lambda-function-permission",
        function=fn_name,
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
    )
    return function

def create_rest_non_proxy(integration_function: aws.lambda_.Function):
    api = aws.apigateway.RestApi("rest-api", 
        name="rest-lambda-non-proxy",
        endpoint_configuration=aws.apigateway.RestApiEndpointConfigurationArgs(
            types="REGIONAL"
    ))
    resource = aws.apigateway.Resource("rest-api-resource",
        parent_id=api.root_resource_id,
        path_part="{city}",
        rest_api=api.id
    )
    # REST API를 위한 model 생성
    model = aws.apigateway.Model("rest-api-model",
        name="GetStartedLambdaIntegrationUserInput",
        rest_api=api.id,
        content_type="application/json",
        schema="""
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "GetStartedLambdaIntegrationInputModel",
    "type": "object",
    "properties": {
        "callerName": { "type": "string" }
    }
}"""
    )
    method = aws.apigateway.Method("rest-api-method",
        authorization="NONE",
        http_method="ANY", # DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
        resource_id=resource.id,
        rest_api=api.id,
        request_parameters={
            "method.request.querystring.time": True,
            "method.request.header.day": True,
        },
        request_models={
            "application/json" : model.name
        },
    )
    aws.apigateway.Integration("rest-api-integration",
        http_method=method.http_method,
        resource_id=resource.id,
        rest_api=api.id,
        type="AWS",
        uri=integration_function.invoke_arn,
        integration_http_method="POST" ,
        request_templates={
            "application/json": """
#set($inputRoot = $input.path('$'))
{
"city": "$input.params('city')",
"time": "$input.params('time')",
"day":  "$input.params('day')",
"name": "$inputRoot.callerName"
}"""
        }   
    )
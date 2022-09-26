import pulumi
import pulumi_aws as aws
import json
import boto3


def create_lambda_function():
    fn_name="lambda-proxy-integration"
    account = boto3.client('sts').get_caller_identity()["Account"]

    # cloudwatch log 그룹에 대한 권한을 포함한 policy 생성
    policy = aws.iam.Policy("role-policy",
        name=fn_name+"-policy",
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
        managed_policy_arns=[policy.arn],
        name=fn_name+"-role",
        description="Lambda execution role with logging permitted",
    )
    function = aws.lambda_.Function("lambda-function",
        name=fn_name,
        code=pulumi.FileArchive("sample.zip"),
        role=role.arn,
        handler="index.handler",
        runtime="nodejs12.x",
        timeout=120,
    )
    return function

def create_rest_proxy(integration_function: aws.lambda_.Function):
    api = aws.apigateway.RestApi("rest-api", 
        name="rest-lambda-proxy",
        endpoint_configuration=aws.apigateway.RestApiEndpointConfigurationArgs(
            types="REGIONAL"
    ))
    resource = aws.apigateway.Resource("rest-api-resource",
        parent_id=api.root_resource_id,
        path_part="hello",
        rest_api=api.id
    )
    method = aws.apigateway.Method("rest-api-method",
        authorization="NONE",
        http_method="ANY", # DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
        resource_id=resource.id,
        rest_api=api.id
    )
    aws.apigateway.Integration("rest-api-integration",
        http_method=method.http_method,
        resource_id=resource.id,
        rest_api=api.id,
        type="AWS_PROXY",
        uri=integration_function.invoke_arn,
        integration_http_method="POST"
    )
    # API Gateway에서 lambda function을 실행할 수 있도록 permisson 추가
    account = boto3.client('sts').get_caller_identity()["Account"]
    aws.lambda_.Permission("lambda-function-permission",
        function=integration_function.name,
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        # source_arn=pulumi.Output.all(api.id, method.http_method, resource.path).apply(lambda id, http_method, path: f"arn:aws:execute-api:us-east-1:{account}:{id}/*/{http_method}{path}"),
    )

############ setup ############

fn = create_lambda_function()
create_rest_proxy(fn)
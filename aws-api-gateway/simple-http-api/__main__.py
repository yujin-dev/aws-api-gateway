import pulumi
import pulumi_aws as aws
import json

def create_dynamodb_table():
    return aws.dynamodb.Table("dynamodb-table",
    name="http-crud-tutorial-items",
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name="id",
            type="S",
        )
    ],
    billing_mode="PROVISIONED",
    hash_key="id",
    read_capacity=5,
    write_capacity=5)

def create_lambda_function():
    fn_name="http-crud-tutorial-function"
    account = boto3.client('sts').get_caller_identity()["Account"]

    # dynamodb 및 cloudwatch log 그룹에 대한 권한을 포함한 policy 생성
    policy = aws.iam.Policy("role-policy",
        name="http-crud-tutorial-role-policy",
        policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "dynamodb:DeleteItem",
                            "dynamodb:GetItem",
                            "dynamodb:PutItem",
                            "dynamodb:Scan",
                            "dynamodb:UpdateItem"
                        ],
                        "Resource": f"arn:aws:dynamodb:us-east-1:{account}:table/*"
                    },
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
        name="http-crud-tutorial-role",
        description="Lambda execution role with logging permitted",
    )
    function = aws.lambda_.Function("lambda-function",
        name=fn_name,
        code=pulumi.FileArchive("sample.zip"), # index.js를 압축한 파일
        role=role.arn,
        handler="index.handler",
        runtime="nodejs12.x",
        timeout=120,
    )
    # API Gateway에서 lambda function을 실행할 수 있도록 permisson 추가
    aws.lambda_.Permission("lambda-function-permission",
        function=fn_name,
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com"
    )
    return function

def create_http_proxy(integration_function):
    api = aws.apigatewayv2.Api("http-api",
            protocol_type="HTTP",
            name="http-crud-tutorial-api"
        )
    # HTTP API의 Stage를 생성하여 배포
    aws.apigatewayv2.Stage("http-api-stage",
        api_id=api.id,
        name = "hello",
        auto_deploy=True
    )
    # integration type = Lambda Function으로 하여 integration 생성
    # *Lambda funcion은 integration_type을 AWS_PROXY로 하여 integration_uri에 lambda function의 invoke_arn을 설정해야 함
    integration = aws.apigatewayv2.Integration("integration", 
        api_id = api.id,
        integration_type="AWS_PROXY",
        integration_uri=integration_function.invoke_arn
    )
    routes = [
        "GET /items/{id}",
        "GET /items",
        "PUT /items",
        "DELETE /items/{id}"
    ]
    [aws.apigatewayv2.Route(key, 
                            api_id=api.id, 
                            route_key=key,
                            target=integration.id.apply(lambda id: f"integrations/{id}")) for key in routes]


############ setup ############

create_dynamodb_table()
create_lambda_function()
create_http_proxy()
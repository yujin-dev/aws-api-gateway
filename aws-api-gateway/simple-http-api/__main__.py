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
        managed_policy_arns=["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],
        name="http-crud-tutorial-role",
        description="Lambda execution role with logging permitted",
    )
    return aws.lambda_.Function("lambda-function",
        name="http-crud-tutorial-function",
        code=pulumi.Archive("sample.zip"),
        role=role.arn,
        handler="index.js",
        runtime="nodejs16.x",
        timeout=120,
    )

def create_http_proxy(integration_function):
    api = aws.apigatewayv2.Api("http-api",
            protocol_type="HTTP",
            name="http-crud-tutorial-api"
        )
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
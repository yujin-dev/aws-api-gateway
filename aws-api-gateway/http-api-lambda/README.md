# Build a CRUD API with Lambda and DynamoDB

[Tutorial: Build a CRUD API with Lambda and DynamoDB](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-dynamo-db.html)를 pulumi로 구현합니다.

![](https://docs.aws.amazon.com/apigateway/latest/developerguide/images/ddb-crud.png)

- HTTP API를 사용하여 API Gateway에서 Lambda 함수로 요청을 라우팅합니다

## Setup
```console
$ pulumi up
```

## Test
1. 샘플 데이터를 삽입합니다
    ```console
    $ curl -v -XPUT -H "Content-Type: application/json" -d "{\"id\": \"123\", \"price\": 12345, \"name\": \"myitem\"}" https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/hello/items

    > PUT /hello/items HTTP/2
    > Host: xxxxxxxxxx.execute-api.us-east-1.amazonaws.com
    > user-agent: curl/7.68.0
    > accept: */*
    > content-type: application/json
    > content-length: 47
    > 
    * Connection state changed (MAX_CONCURRENT_STREAMS == 128)!
    * We are completely uploaded and fine
    < HTTP/2 200 
    ..
    * Connection #0 to host xxxxxxxxxx.execute-api.us-east-1.amazonaws.com left intact
    "Put item 124"% 
    ```

2. 전체 데이터를 확인합니다
    ```console
    $ curl -v https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/hello/items

    > GET /hello/items HTTP/2
    ...
    * Connection #0 to host xxxxxxxxxx.execute-api.us-east-1.amazonaws.com left intact
    {"Items":[{"price":12345,"id":"123","name":"myitem"},{"price":12345,"id":"124","name":"myitem"}],"Count":2,"ScannedCount":2}%
    ```

3. `id=123`에 대해 결과를 확인합니다
    ```console
    $ curl -v https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/hello/items/123

    > GET /hello/items/123 HTTP/2
    ...
    {"Item":{"price":12345,"id":"124","name":"myitem"}}%
    ```

## Clean up
```console
$ pulumi destroy
```

### Considerations
AWS 콘솔에서 Lambda에서 서비스 실행을 위한 role template을 Simple microservice permissions으로 설정하면 다음과 같은 형태입니다.
```json
    {
      "Sid": "xxxxxx",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:{region}:{account}:function:http-crud-tutorial-function",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:execute-api:{region}:{account}:{api-id}/*/*/items"
        }
      }
    }
```

- Role에 부여되어 생성되는 policy에 SourceARN을 조건에 추가하여 요청 주체의 리소스의 ARN을 비교합니다
# Build an API Gateway REST API with Lambda integration - Proxy

[Tutorial: Build a Hello World REST API with Lambda proxy integration](https://docs.aws.amazon.com/ko_kr/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html)를 pulumi로 구현합니다.

**Lambda proxy integration**에서는 lambda 함수에 대한 input을 equest headers / path variables / query string parameters / body를 조합하여 사용합니다.


## Test
```console
$ curl -v -X POST \
  'https://bic0v5uvn0.execute-api.us-east-1.amazonaws.com/test/hello?name=John&city=Seattle' \
  -H 'content-type: application/json' \
  -H 'day: Thursday' \
  -d '{ "time": "evening" }'
```
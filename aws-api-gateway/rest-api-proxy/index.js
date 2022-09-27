'use strict';
console.log('Loading hello world function');
 
exports.handler = async (event) => {
    let name = "you";
    let city = 'World';
    let time = 'day';
    let day = '';
    let responseCode = 200;
    console.log("request: " + JSON.stringify(event));
    
    if (event.queryStringParameters && event.queryStringParameters.name) {
        console.log("Received name: " + event.queryStringParameters.name);
        name = event.queryStringParameters.name;
    }
    
    if (event.queryStringParameters && event.queryStringParameters.city) {
        console.log("Received city: " + event.queryStringParameters.city);
        city = event.queryStringParameters.city;
    }
    
    if (event.headers && event.headers['day']) {
        console.log("Received day: " + event.headers.day);
        day = event.headers.day;
    }
    
    if (event.body) {
        let body = JSON.parse(event.body)
        if (body.time) 
            time = body.time;
    }
 
    let greeting = `Good ${time}, ${name} of ${city}.`;
    if (day) greeting += ` Happy ${day}!`;

    let responseBody = {
        message: greeting,
        input: event
    };
    
    // Lambda proxy integration에서 결과값은 반드시 JSON 형식이어야 함
    // headers : custom response header 
    // body : JSON
    // base64-encoded payload의 경우 isBase64Encoded = True로 설정해야 함
    let response = {
        statusCode: responseCode,
        headers: {
            "x-custom-header" : "my custom header value"
        },
        body: JSON.stringify(responseBody)
    };
    console.log("response: " + JSON.stringify(response))
    return response;
};
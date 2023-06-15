resource "aws_api_gateway_rest_api" "api_gateway_rest_api" {
  name = "api_gateway_rest_api"
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "rest-api"
      version = "1.0"
    }
    paths =  var.api_paths
  })
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  
}
resource "aws_api_gateway_deployment" "api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.api_gateway_rest_api.body))
  }
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_api_gateway_stage" "api_gateway_stage" {
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name    = "stage"
}
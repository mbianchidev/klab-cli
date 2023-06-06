resource "aws_api_gateway_rest_api" "api_gateway_rest_api" {
  name = "{{ api_gateway_name | default("api_gateway_rest_api") }}"

  body = jsonencode({
    openapi = "{{ openapi_version | default("3.0.1") }}"
    info = {
      title   = "{{ api_title | default("rest-api")}}"
      version = "{{ api_version | default("1.0")}}"
    }
    paths = {
      {%- for path in paths %}
      "{{ path.path_name }}" = {
        "{{ path.method }}" = {
          {{ path.integration_key }} = {
            httpMethod           = "{{ path.httpMethod }}"
            payloadFormatVersion = "{{ path.payloadFormatVersion }}"
            type                 = "{{ path.type }}"
            uri                  = "{{ path.uri}}"
          }
        }
      },
      {%- endfor %}
    }
  })

  {% if endpoint_configuration %}
  endpoint_configuration {
    types = ["{{ endpoint_configuration }}"]
  }
  {% endif %}
}

resource "aws_api_gateway_deployment" "api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.api_gateway_rest_api.body))
  }

  lifecycle {
    create_before_destroy = {{ create_before_destroy | default("true") }}
  }
}

resource "aws_api_gateway_stage" "api_gateway_stage" {
  deployment_id = aws_api_gateway_deployment.api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name    = "{{ api_gateway_stage_name | default("stage") }}"
}

output "api_gateway_url" {
  value = aws_api_gateway_stage.api_gateway_stage.invoke_url
}
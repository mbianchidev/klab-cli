variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "api_gateway_rest_api"
}

variable "api_paths" {
  description = "Map of API paths and integrations"
  type        = map(any)
  default = {
    "/path1" = {
      "get" = {
        "httpMethod"           = "GET"
        "payloadFormatVersion" = "1.0"
        "type"                 = "HTTP_PROXY"
        "uri"                  = "https://ip-ranges.amazonaws.com/ip-ranges.json"
      }
    },
    "/path2" = {
      "get" = {
        "httpMethod"           = "GET"
        "payloadFormatVersion" = "1.0"
        "type"                 = "HTTP_PROXY"
        "uri"                  = "https://ip-ranges.amazonaws.com/ip-ranges.json"
      }
    }
  }
}
variable "endpoint_types" {
  description = "Types of endpoint configuration"
  type        = list(string)
  default     = ["REGIONAL"]
}
variable "stage_name" {
  description = "Variable for stage name of the api gateway uri"
  default = "stage"
}

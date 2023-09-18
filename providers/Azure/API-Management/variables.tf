##### RESOURCE GROUP #####

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
  default     = "example-resources-or-smth"
}

variable "resource_group_location" {
  description = "The location of the resource group."
  type        = string
  default     = "West Europe"
}

##### API MANAGEMENT #####
variable "api_management_name" {
  description = "The name of the API management instance."
  type        = string
  default     = "kubelab-apim"
}

variable "api_management_publisher_name" {
  default = "Kubelab"
}

variable "api_management_publisher_email" {
  default = "daniel@kubelab.cloud"
}

variable "api_management_sku_name" {
  default = "Developer_1"
}

##### APIS #####

variable "api_name" {
  default = "kubelab-api2"
}

variable "api_revision" {
  default = "1"
}

variable "api_display_name" {
  default = "NGINX API"
}

variable "api_path" {
  default = "nginx"
}

variable "api_protocols" {
  default = ["https", "http"]
}

variable "api_service_url" {
  default = "http://20.101.230.9/"
}

variable "api_content_format" {
  default = "openapi+json"
}

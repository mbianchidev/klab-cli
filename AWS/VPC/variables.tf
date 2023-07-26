variable "vpc_cidr_block" {
  description = "VPC cidr block"
  default     = "192.168.0.0/16"
}

variable "subnet_public" {
  description = "Variable for public subnets"
  default = {
    _1 = {
      cidr_block        = "192.168.0.0/18"
      availability_zone = "eu-west-1a"
    }
    _2 = {
      cidr_block        = "192.168.64.0/18"
      availability_zone = "eu-west-1b"
    }
  }
}

variable "region" {
  type = string
}

variable "subnet_private" {
  description = "Variable for private subnets"
  default = {
    _1 = {
      cidr_block = "192.168.192.0/18"
    }
    _2 = {
      cidr_block = "192.168.128.0/18"
    }
  }
}

variable "availability_zones" {
  type        = list(string)
  description = "A list of availability zones for the subnets"
}
variable "custom_ports" {
  description = "Custom ports to open on security groups"
  type        = map(any)
  default = {
    22   = ["0.0.0.0/0"]
    2049 = ["0.0.0.0/0"]
    80   = ["0.0.0.0/0"]
    443  = ["0.0.0.0/0"]
  }
}

variable "environment" {
  type    = string
  default = "testing"
}

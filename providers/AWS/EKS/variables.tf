
variable "vpc_public_subnet_1" {
  description = "Public Subnet ID for EKS"
  type        = list(string)
}
variable "vpc_private_subnet_1" {
  description = "Private Subnet ID for EKS"
  type        = list(string)
}
variable "vpc_security_group" {
  description = "security_group ID for EKS"
  type        = string
}
variable "endpoint_private_access" {
  description = "Variable for endpoint_private_access"
  default = false 
}
variable "endpoint_public_access" {
  description = "Variable for endpoint_public_access"
  default = true
}
variable "ami_type" {
  description = "Variable for AMI type"
  default =   "AL2_x86_64"
}
variable "capacity_type" {
  description = "Variable for capacity type"
  default =   "ON_DEMAND"
}
variable "disk_size" {
  description = "Variable for disk size"
  default =   20
}
variable "instance_type" {
  description = "Variable for instance type"
  default = "t3.medium"
}
##### Networking Variables #####

variable "network" {
  description = "The VPC network created to host the cluster in."
  type        = string
  default     = "gke-network"
}

variable "subnetwork" {
  description = "The subnetwork created to host the cluster in."
  type        = string
  default     = "gke-subnet"
}

variable "subnet_ip_cidr" {
  description = "IP CIDR to use for the subnet."
  type        = string
  default     = "10.10.0.0/16"
}

variable "gke_ip_range_pods_name" {
  description = "The secondary IP range name to use for pods."
  type        = string
  default     = "ip-range-pods"
}

variable "ip_cidr_range_pods" {
  description = "The secondary IP CIDR range to use for the pods."
  type        = string
  default     = "10.20.0.0/16"
}

variable "gke_ip_range_services_name" {
  description = "The secondary IP range name to use for services."
  type        = string
  default     = "ip-range-services"
}

variable "ip_cidr_range_services" {
  description = "The secondary IP range CIDR to use for services."
  type        = string
  default     = "10.30.0.0/16"
}

# Global variables

variable "region" {
  type = string
}

variable "project" {
  type = string
}
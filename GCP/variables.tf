variable "cluster_name" {
  description = "The name for the GKE cluster"
  type        = string
}

variable "project" {
  description = "The project ID."
  type        = string
}

variable "region" {
  description = "The region for the infrastructure."
  type        = string
}

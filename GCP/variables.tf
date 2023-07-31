variable "cluster_name" {
  description = "The name for the GKE cluster"
  default     = "gke"
  type        = string
}

variable "project" {
  description = "The project ID."
  type        = string
}

variable "region" {
  description = "The region for the infrastructure."
  default     = "europe-central2"
  type        = string
}

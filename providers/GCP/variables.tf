variable "cluster_name" {
  description = "The name for the GKE cluster"
  default     = "gke-terraform"
  type        = string
}

variable "project_id" {
  description = "The project ID."
  default     = "cts-project-388707"
  type        = string
}

variable "region" {
  description = "The region for the infrastructure."
  default     = "us-central1"
  type        = string
}

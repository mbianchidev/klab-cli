variable "region" {
  type        = string
  description = "Region in which you like to deploy the CodePipeline"
  default     = "eu-west-1"
}

variable "github_owner" {
  type        = string
  description = "GitHub repository owner"
  default = "KubeLab-cloud"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository name"
  default = "kubelab-middleware"
}

variable "github_branch" {
  type        = string
  description = "GitHub branch name"
  default = "main"
}

variable "github_oauth_token" {
  type        = string
  description = "GitHub OAuth token"
}
variable "env" {
  description = "Variable for "
  default = "dev"
}
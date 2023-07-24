variable "user_principal_name" {
  description = "Azure AD user principal name"
  type        = string
  default     = "daniel@kubelab.cloud"
}

variable "rotation_days" {
  description = "Number of days for rotation"
  type        = number
  default     = 7
}

variable "application_display_name" {
  description = "Display name for the Azure AD Application"
  type        = string
}

variable "service_principal_app_role_assignment_required" {
  description = "Whether app role assignment is required for the Azure AD Service Principal"
  type        = bool
  default     = false
}

variable "service_principal_password_display_name" {
  description = "Display name for the service principal password"
  type        = string
}

variable "application_password_display_name" {
  description = "Display name for the application password"
  type        = string
}

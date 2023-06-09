terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.41.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.36.0"
    }
  }
}

locals {
  owners = [
    data.azuread_user.owner.object_id
  ]
}

resource "azuread_application" "aks_application" {
  display_name = "AKS Cluster Application"
  owners       = local.owners
}

resource "azuread_service_principal" "aks_service_principal" {
  application_id               = azuread_application.aks_application.application_id
  app_role_assignment_required = false
  owners                       = local.owners
}

data "azuread_user" "owner" {
  user_principal_name = "daniel@kubelab.cloud"
}

resource "time_rotating" "one_week" {
  rotation_days = 7
}

resource "azuread_service_principal_password" "sp_password" {
  display_name         = "The service principal password"
  service_principal_id = azuread_service_principal.aks_service_principal.object_id
  rotate_when_changed = {
    rotation = time_rotating.one_week.id
  }
}

resource "azuread_application_password" "app_password" {
  display_name = "The app password"
  application_object_id = azuread_application.aks_application.object_id
  rotate_when_changed = {
    rotation = time_rotating.one_week.id
  }
}

output "sp_cliend_secret" {
  value = azuread_service_principal_password.sp_password.value
  sensitive = true
}

output "app_client_secret" {
  value = azuread_application_password.app_password.value
  sensitive = true
}
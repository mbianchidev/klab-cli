locals {
  owners = [
    data.azuread_user.owner.object_id
  ]
}

data "azuread_user" "owner" {
  user_principal_name = var.user_principal_name
}

resource "time_rotating" "one_week" {
  rotation_days = var.rotation_days
}

resource "azuread_application" "application" {
  display_name = var.application_display_name
  owners       = local.owners
}

resource "azuread_service_principal" "service_principal" {
  application_id               = azuread_application.application.application_id
  app_role_assignment_required = var.service_principal_app_role_assignment_required
  owners                       = local.owners
}

resource "azuread_service_principal_password" "service_principal_password" {
  display_name         = var.service_principal_password_display_name
  service_principal_id = azuread_service_principal.service_principal.object_id
  rotate_when_changed = {
    rotation = time_rotating.one_week.id
  }
}

resource "azuread_application_password" "application_password" {
  display_name          = var.application_password_display_name
  application_object_id = azuread_application.application.object_id
  rotate_when_changed = {
    rotation = time_rotating.one_week.id
  }
}

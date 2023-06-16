
resource "azurerm_resource_group" "storage" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

provider "azurerm" {
  features {}
}

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.storage.name
  location                 = azurerm_resource_group.storage.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_account_replication_type

  tags = var.tags

  network_rules {
    default_action = "Deny"
  }
}

resource "azurerm_storage_container" "container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = var.container_access_type
}

output "storage_account_id" {
  value = azurerm_storage_account.storage.id
}

output "container_name" {
  value = azurerm_storage_container.container.name
}
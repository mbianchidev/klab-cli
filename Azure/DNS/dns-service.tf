terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "dns_service_resource_group" {
  count    = var.use_existing_resource_group ? 0 : 1
  name     = var.resource_group_name
  location = var.resource_group_location
}

data "azurerm_resource_group" "existing" {
  count      = var.use_existing_resource_group ? 1 : 0
  name       = var.resource_group_name
  depends_on = [azurerm_resource_group.dns_service_resource_group]
}

resource "azurerm_dns_zone" "dns_zone" {
  name                = var.dns_zone_name
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
}

resource "azurerm_dns_a_record" "main_dns_a_record" {
  name                = var.main_dns_a_record_name
  zone_name           = azurerm_dns_zone.dns_zone.name
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  ttl                 = var.main_dns_a_record_ttl
  records             = [var.main_dns_a_record_ip_address]
}

resource "azurerm_dns_a_record" "subdomain_dns_a_record" {
  for_each            = var.subdomains
  name                = each.value.subdomain_name
  zone_name           = azurerm_dns_zone.dns_zone.name
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  ttl                 = each.value.subdomain_ttl
  records             = [each.value.subdomain_records]
}

resource "azurerm_dns_ns_record" "dns_ns_record" {
  count               = var.add_ns_record ? 1 : 0
  name                = var.dns_ns_record_name
  zone_name           = azurerm_dns_zone.dns_zone.name
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  ttl                 = var.dns_ns_ttl
  records             = var.dns_ns_records
}

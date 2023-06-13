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

resource "azurerm_resource_group" "created_resource_group" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

resource "azurerm_api_management" "api_management" {
  name                = var.api_management_name
  location            = azurerm_resource_group.created_resource_group.location
  resource_group_name = azurerm_resource_group.created_resource_group.name
  publisher_name      = var.api_management_publisher_name
  publisher_email     = var.api_management_publisher_email

  sku_name = var.api_management_sku_name
}

resource "azurerm_api_management_api" "kubernetes_nginx_api" {
  name                = var.api_name
  resource_group_name = azurerm_resource_group.created_resource_group.name
  api_management_name = azurerm_api_management.api_management.name
  revision            = var.api_revision
  display_name        = var.api_display_name
  path                = var.api_path
  protocols           = var.api_protocols
  service_url         = var.api_service_url

  import {
    content_format = "openapi+json"
    content_value  = "${file("${path.module}/API/kubernetes_nginx_api.json")}"
  }
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "resource_group_location" {
  value = azurerm_resource_group.rg.location
}

output "akspodssubnet" {
  value = azurerm_subnet.akspodssubnet.id
}

provider "azurerm" {
  features {}
}

module "aks" {
  source  = "Azure/aks/azurerm"
  version = "6.2.0"

  prefix              = var.prefix
  resource_group_name = var.resource_group_name
  cluster_name        = var.cluster_name
  location            = var.location
  kubernetes_version  = var.kubernetes_version
  agents_count        = var.node_count
  agents_size         = var.node_vm_size
  enable_auto_scaling = var.enable_auto_scaling
  agents_min_count    = var.min_node_count
  agents_max_count    = var.max_node_count
}
locals {
  credentials_file = file("../kubelab-cli/credentials/azure_kube_credential")
  credentials      = jsondecode(local.credentials_file)
}

provider "azurerm" {
  features {}

  subscription_id = local.credentials.id
  tenant_id       = local.credentials.tenantId
}

# module "VNet" {
#   source = "./VNet"
# }

# module "AKS" {
#   source                  = "./AKS-Self-Managed"
#   resource_group_location = module.VNet.resource_group_location
#   resource_group_name     = module.VNet.resource_group_name
#   akspodssubnet_id        = module.VNet.akspodssubnet
# }

module "AKS" {
  source              = "./AKS-Microsoft-Managed"
  resource_group_name = var.resource_group
  prefix              = "testing"
  cluster_name        = var.cluster_name
  location            = var.location
  kubernetes_version  = "1.26"
  enable_auto_scaling = true
  node_vm_size        = "Standard_D2s_v3"
  node_count          = null
  min_node_count      = 1
  max_node_count      = 2
}

variable "resource_group" {
  type = string
  default = "kubelab_resource_group"
}

variable "cluster_name" {
  type = string
  default = "aks"
}

variable "location" {
  type = string
  default = "eastus"
}

output "cluster_name" {
  value = module.AKS.cluster_name
}

output "cluster_region" {
  value = module.AKS.cluster_region
}

output "cluster_resource_group" {
  value = module.AKS.resource_group_name
}

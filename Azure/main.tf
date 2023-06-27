locals {
  credentials_file = file("../kubelab-cli/credentials/azure_kube_credential.json")
  credentials      = jsondecode(local.credentials_file)
}

provider "azurerm" {
  features {}

  subscription_id = local.credentials.id
  tenant_id       = local.credentials.tenantId
}

module "VNet" {
  source = "./VNet"
}

module "AKS" {
  source                  = "./AKS"
  resource_group_location = module.VNet.resource_group_location
  resource_group_name     = module.VNet.resource_group_name
  akspodssubnet_id        = module.VNet.akspodssubnet
}

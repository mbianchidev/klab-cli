module "VNet" {
  source = "./VNet"
}
module "AKS" {
  source = "./AKS"
  resource_group_location = module.VNet.resource_group_location
  resource_group_name = module.VNet.resource_group_name
  akspodssubnet_id = module.VNet.akspodssubnet
}
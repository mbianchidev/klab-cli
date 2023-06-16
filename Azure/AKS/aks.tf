provider "azurerm" {
  features {}
}


resource "azurerm_kubernetes_cluster" "k8s" {
  name                = var.cluster_name
  location            = var.resource_group_location
  resource_group_name = var.resource_group_name # th RG the single cluster entity goes is
  dns_prefix          = "k8s"
  node_resource_group = "K8S${var.resource_group_name}"  #  all the k8s' entities must be in fdifferent RG than where the cluster object itself is
  kubernetes_version = "1.26.3"

  default_node_pool {
    name                  = var.default_node_name
    type                  = "AvailabilitySet"
    vm_size               = var.vmsize # Standard_DC2s_v2 Standard_B1ms
    enable_node_public_ip = false
    enable_auto_scaling   = false
    os_disk_size_gb       = var.disk_size
    node_count            = var.node_count
    vnet_subnet_id        = var.akspodssubnet_id
  }

  identity {
    type = "SystemAssigned"
  }
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = var.aksservicecidr
    dns_service_ip    = var.aksdns
  }
  
}

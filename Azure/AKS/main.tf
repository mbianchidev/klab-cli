provider "azurerm" {
  features {}
}
resource "azurerm_resource_group" "rg" {
    name            = var.rgname
    location        = var.location
    
}

resource "azurerm_virtual_network" "vnet" {
    name                        = "vnet"
    location                    = azurerm_resource_group.rg.location
    resource_group_name         = azurerm_resource_group.rg.name
    address_space               = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "vmsubnet" {
    name                        = "vmsubnet"
    resource_group_name         = azurerm_resource_group.rg.name
    virtual_network_name        = azurerm_virtual_network.vnet.name
    address_prefixes            = [var.vmsubnet]
}
resource "azurerm_network_security_group" "nsg-1" {
  name                = "nsg-1"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  
  dynamic "security_rule" {
    for_each = var.nsg_rules
    content {
      name                       = security_rule.value.name
      priority                   = security_rule.value.priority
      direction                  = security_rule.value.direction
      access                     = security_rule.value.access
      protocol                   = security_rule.value.protocol
      source_port_range          = security_rule.value.source_port_range
      destination_port_range     = security_rule.value.destination_port_range
      source_address_prefix      = security_rule.value.source_address_prefix
      destination_address_prefix = security_rule.value.destination_address_prefix
    }
  }
  
}

resource "azurerm_subnet_network_security_group_association" "subnet-1" {
  subnet_id                 = azurerm_subnet.vmsubnet.id
  network_security_group_id = azurerm_network_security_group.nsg-1.id
}
resource "azurerm_subnet" "akspodssubnet" {
    name                        = "akspodssubnet"
    resource_group_name         = azurerm_resource_group.rg.name
    virtual_network_name        = azurerm_virtual_network.vnet.name
    address_prefixes            = [var.akspodssubnet]
}


resource "azurerm_kubernetes_cluster" "k8s" {
  name                = var.cluster_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name # th RG the single cluster entity goes is
  dns_prefix          = "k8s"
  node_resource_group = "K8S${azurerm_resource_group.rg.name}"  #  all the k8s' entities must be in fdifferent RG than where the cluster object itself is
  kubernetes_version = "1.26.3"

  default_node_pool {
    name                  = var.default_node_name
    type                  = "AvailabilitySet"
    vm_size               = var.vmsize # Standard_DC2s_v2 Standard_B1ms
    enable_node_public_ip = false
    enable_auto_scaling   = false
    os_disk_size_gb       = var.disk_size
    node_count            = var.node_count
    vnet_subnet_id        = azurerm_subnet.akspodssubnet.id
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

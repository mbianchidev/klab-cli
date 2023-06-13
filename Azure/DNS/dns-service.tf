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

variable "use_existing_resource_group" {
  description = "Flag to indicate whether to use an existing resource group or create a new one"
  type        = bool
  default     = false
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
  name                = var.dns_ns_record_name
  zone_name           = azurerm_dns_zone.dns_zone.name
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  ttl                 = var.dns_ns_ttl
  records             = var.dns_ns_records
}

resource "azurerm_virtual_network" "example" {
  name                = "example-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.dns_service_resource_group[0].location
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
}

resource "azurerm_subnet" "example" {
  name                 = "example-subnet"
  resource_group_name  = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.0.0/24"]
}

resource "azurerm_public_ip" "example" {
  name                = "example-public-ip"
  location            = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.dns_service_resource_group[0].location
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "example" {
  name                = "example-nsg"
  location            = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.dns_service_resource_group[0].location
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
}

resource "azurerm_network_security_rule" "example" {
  name                        = "example-nsg-rule"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "80"
  destination_address_prefix  = "*"
  source_address_prefixes     = ["0.0.0.0/0"]
  resource_group_name         = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  network_security_group_name = azurerm_network_security_group.example.name
}

resource "azurerm_network_interface" "example" {
  name                = "example-nic"
  location            = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.dns_service_resource_group[0].location
  resource_group_name = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name

  ip_configuration {
    name                          = "example-nic-config"
    subnet_id                     = azurerm_subnet.example.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.example.id
  }
}

resource "azurerm_linux_virtual_machine" "example" {
  name                            = "example-vm"
  location                        = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].location : azurerm_resource_group.dns_service_resource_group[0].location
  resource_group_name             = var.use_existing_resource_group ? data.azurerm_resource_group.existing[0].name : azurerm_resource_group.dns_service_resource_group[0].name
  size                            = "Standard_DS1_v2"
  admin_username                  = "adminuser"
  disable_password_authentication = false # Enable password authentication

  admin_password = "YourAdminPassword123Here" # Add the admin password here (satisfying complexity requirements)

  network_interface_ids = [azurerm_network_interface.example.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  custom_data = base64encode(<<EOF
#!/bin/bash
sudo apt-get update
sudo apt-get install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
EOF
  )
}

output "public_ip" {
  value = azurerm_public_ip.example.ip_address
}

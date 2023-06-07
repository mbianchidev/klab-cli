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

{% if existing_resource_group == true %}
data "azurerm_resource_group" "existing_resource_group" {
  name = "{{ resource_group_name }}"
}
{%- else %}
resource "azurerm_resource_group" "created_resource_group" {
  name     = "{{ resource_group_name }}"
  location = "{{resource_group_location}}"
}
{%- endif %}

{% for nsg in nsgs %}
resource "azurerm_network_security_group" "{{ nsg.nsg_name }}" {
  name                = "{{ nsg.nsg_name }}"
  {%- if existing_resource_group %}
  location            = data.azurerm_resource_group.existing_resource_group.location
  resource_group_name = data.azurerm_resource_group.existing_resource_group.name
  {%- else %}
  location            = azurerm_resource_group.created_resource_group.location
  resource_group_name = azurerm_resource_group.created_resource_group.name
  {%- endif %}

  {% for security_rule in nsg.security_rules %}
  security_rule {
    name                       = "{{ security_rule.name }}"
    priority                   = "{{ security_rule.priority }}"
    direction                  = "{{ security_rule.direction }}"
    access                     = "{{ security_rule.access }}"
    protocol                   = "{{ security_rule.protocol }}"
    source_port_range          = "{{ security_rule.source_port_range}}"
    destination_port_range     = "{{ security_rule.destination_port_range }}"
    source_address_prefix      = "{{ security_rule.source_address_prefix }}"
    destination_address_prefix = "{{ security_rule.destination_address_prefix }}"
  }
  {% endfor %}
}
{% endfor %}

resource "azurerm_virtual_network" "example" {
  name                = "{{ vnet_name | default("azure-vnet") }}"
  {%- if existing_resource_group %}
  location            = data.azurerm_resource_group.existing_resource_group.location
  resource_group_name = data.azurerm_resource_group.existing_resource_group.name
  {%- else %}
  location            = azurerm_resource_group.created_resource_group.location
  resource_group_name = azurerm_resource_group.created_resource_group.name
  {%- endif %}
  address_space       = ["10.0.0.0/16"]
  dns_servers         = ["10.0.0.4", "10.0.0.5"]

  tags = {
    environment = "Production"
  }
}

resource "azurerm_subnet" "example" {
  name                 = "example-subnet"
  {%- if existing_resource_group %}
  resource_group_name = data.azurerm_resource_group.existing_resource_group.name
  {%- else %}
  resource_group_name = azurerm_resource_group.created_resource_group.name
  {%- endif %}
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "delegation"

    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action", "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action"]
    }
  }
}

resource "azurerm_subnet_network_security_group_association" "example" {
  subnet_id                 = azurerm_subnet.example.id
  network_security_group_id = azurerm_network_security_group.nsg-1.id
}

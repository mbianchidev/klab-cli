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
data "azurerm_resource_group" "{{ resource_group | default("existing_resource_group") }}" {
  name = "{{ resource_group_name }}"
}
{%- else %}
resource "azurerm_resource_group" "{{ resource_group | default("created_resource_group") }}" {
  name     = "{{ resource_group_name }}"
  location = "{{resource_group_location}}"
}
{%- endif %}

resource "azurerm_virtual_network" "{{ vnet_name }}" {
  name                = "{{ vnet_name }}"
  {%- if existing_resource_group %}
  location            = data.azurerm_resource_group.{{ resource_group | default("existing_resource_group") }}.location
  resource_group_name = data.azurerm_resource_group.{{ resource_group | default("existing_resource_group") }}.name
  {%- else %}
  location            = azurerm_resource_group.{{ resource_group | default("created_resource_group") }}.location
  resource_group_name = azurerm_resource_group.{{ resource_group | default("created_resource_group") }}.name
  {%- endif %}
  address_space       = {{ vnet_address_space | default('["10.0.0.0/16"]') | safe }}
  dns_servers         = {{ vnet_dns_servers | default('["10.0.0.4", "10.0.0.5"]') | safe }}
}

{% for subnet in subnets %}
resource "azurerm_subnet" "{{ subnet.name }}" {
  name                 = "{{ subnet.name }}"
  {%- if existing_resource_group %}
  resource_group_name = data.azurerm_resource_group.{{ resource_group | default("existing_resource_group") }}.name
  {%- else %}
  resource_group_name = azurerm_resource_group.{{ resource_group | default("created_resource_group") }}.name
  {%- endif %}
  virtual_network_name = azurerm_virtual_network.{{ vnet_name }}.name
  address_prefixes     = {{ subnet.address_prefixes | safe }}
}

{% if subnet.nsg_name is defined %}
resource "azurerm_network_security_group" "{{ subnet.nsg_name }}" {
  name                = "{{ subnet.nsg_name }}"
  {%- if existing_resource_group %}
  location            = data.azurerm_resource_group.{{ resource_group | default("existing_resource_group") }}.location
  resource_group_name = data.azurerm_resource_group.{{ resource_group | default("existing_resource_group") }}.name
  {%- else %}
  location            = azurerm_resource_group.{{ resource_group | default("created_resource_group") }}.location
  resource_group_name = azurerm_resource_group.{{ resource_group | default("created_resource_group") }}.name
  {%- endif %}

  {% for security_rule in subnet.security_rules %}
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

resource "azurerm_subnet_network_security_group_association" "{{ subnet.name }}" {
  subnet_id                 = azurerm_subnet.{{ subnet.name }}.id
  network_security_group_id = azurerm_network_security_group.{{ subnet.nsg_name}}.id
}
{% endif %}

{%- endfor %}

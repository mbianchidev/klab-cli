variable "rgname" {
    default = "aks-tg"
}
variable "cluster_name" {
  default = "K8Scluster"
}
variable "default_node_name" {
  default = "node1"
}
variable "node_count" {
  default = 1
}
variable "disk_size" {
  default = 30
}
variable "location" {
  default = "eastus"
}
variable "vmsubnet" {
  default = "10.0.0.0/24"
}
variable "akspodssubnet" {
  default = "10.0.3.0/24"
}
variable "aksservicecidr" {
  default = "10.1.0.0/16"
}
variable "dockercidrip" {
  default = "172.17.0.1/16"
}
variable "aksdns" {
  default = "10.1.0.10"
}
variable "vmsize" {
  default = "Standard_DS2_v2"
}
variable "nsg_rules" {
  description = "List of security rules for the network security group"
  type        = list(object({
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }))
  default = [
    {
      name                       = "nsg-web_port"
      priority                   = 100
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "80"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    },
    {
      name                       = "nsg-ssh"
      priority                   = 200
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = "22"
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
  ]
}

variable "akspodssubnet_id" {
  description = "AKS Pod Subnet ID"
}
variable "resource_group_name" {
  description = "Resource group name"
}
variable "resource_group_location" {
  description = "Resource group location"
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
variable "vmsize" {
  default = "Standard_DS2_v2"
}
variable "aksdns" {
  default = "10.1.0.10"
}
variable "aksservicecidr" {
  default = "10.1.0.0/16"
}
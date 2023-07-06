variable "prefix" {
  type        = string
  description = "The prefix for the resources created in the specified Azure Resource Group"
}

variable "resource_group_name" {
  description = "Name of the resource group in which AKS will be created."
  type        = string
}

variable "cluster_name" {
  description = "Name of the AKS cluster."
  type        = string
}

variable "location" {
  description = "Azure region where the AKS cluster will be deployed."
  type        = string
}

variable "kubernetes_version" {
  description = "Version of Kubernetes to use for the AKS cluster."
  type        = string
}

variable "node_count" {
  description = "Number of nodes in the AKS cluster."
  type        = number
}

variable "node_vm_size" {
  description = "Virtual machine size for AKS nodes."
  type        = string
}

variable "enable_auto_scaling" {
  description = "Enable or disable auto scaling for the AKS cluster."
  type        = bool
}

variable "min_node_count" {
  description = "Minimum number of nodes when auto scaling is enabled."
  type        = number
}

variable "max_node_count" {
  description = "Maximum number of nodes when auto scaling is enabled."
  type        = number
}

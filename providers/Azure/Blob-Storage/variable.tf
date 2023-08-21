# variables.tf

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
  default     = "MyStorageAccount"
}

variable "resource_group_location" {
  description = "The Azure region where the resource group will be created."
  type        = string
  default     = "West Europe"
}

variable "storage_account_name" {
  description = "The name of the storage account."
  type        = string
  default     = "danielkubelabstorage"
}

variable "storage_account_tier" {
  description = "The storage account tier."
  type        = string
  default     = "Standard"
}

variable "storage_account_replication_type" {
  description = "The storage account replication type."
  type        = string
  default     = "LRS"
}

variable "container_name" {
  description = "The name of the storage container."
  type        = string
  default     = "my-container"
}

variable "container_access_type" {
  description = "The access type for the storage container."
  type        = string
  default     = "private"
}

variable "tags" {
  description = "A map of tags to assign to the resource."
  type        = map(string)
  default     = {
    environment = "dev"
  }
}
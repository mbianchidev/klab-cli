##### Resource Group #####

variable "resource_group_location" {
  description = "The location of the resource group."
  type        = string
  default     = "West Europe"
}

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
  default     = "example-resources-for-dns"
}

##### DNS Service #####

variable "dns_zone_name" {
  description = "The DNS zone name"
  default     = "redkube.cloud"
  type        = string
}

##### Main A Record #####

variable "main_dns_a_record_name" {
  description = "The DNS record name"
  default     = "www"
  type        = string
}

variable "main_dns_a_record_ttl" {
  description = "The time-to-live (TTL) value for the DNS record"
  default     = 300
  type        = number
}

variable "main_dns_a_record_ip_address" {
  description = "The IP address associated with the DNS record"
  default     = "20.16.124.234"
  type        = string
}

##### Subdomains #####

variable "subdomains" {
  default = {
    subdomain-1 = {
      subdomain_name = "sub"
      subdomain_ttl = 60
      subdomain_records = "20.16.124.234"
    }
    subdomain-2 = {
      subdomain_name = "subb"
      subdomain_ttl = 60
      subdomain_records = "20.16.124.234"
    }
  }
}

##### NS Records #####

variable "dns_ns_record_name" {
  description = "NS Record Name"
  type        = string
  default     = "NS-Record"
}

variable "dns_ns_records" {
  description = "List of NS records"
  type        = list(string)
  default     = [
    "ns1-33.azure-dns.com.",
    "ns2-33.azure-dns.net.",
    "ns3-33.azure-dns.org.",
    "ns4-33.azure-dns.info."
  ]
}

variable "dns_ns_ttl" {
  description = "TTL (Time To Live) for the DNS NS record"
  type        = number
  default     = 60
}
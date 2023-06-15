variable "region" {
  default = "eu-west-1"
  type    = string
}

variable "enable_private_zone" {
  default = false
  type    = bool
}

variable "zone_domain_name" {
  default = "redkube.cloud"
  type    = string
}

variable "vpc_id" {
  default = "vpc-12345678"
  type    = string
}

variable "vpc_region" {
  default = "eu-west-1"
  type    = string
}

##### Zone Domain #####

variable "zone_domain_ip" {
  type    = string
  default = "3.227.247.127"
}

variable "zone_domain_ttl" {
  type    = number
  default = 600
}

##### Subdomains #####

variable "with_subdomains" {
  type    = bool
  default = true
}

variable "subdomain" {
  default = {
    subdomain1 = {
      subdomain_name = "first"
      subdomain_ttl  = 300
      subdomain_ip   = "3.227.247.127"
    }
    subdomain2 = {
      subdomain_name = "second"
      subdomain_ttl  = 300
      subdomain_ip   = "3.227.247.127"
    }
  }
}

##### NS Record #####

variable "with_ns_record" {
  default = false
}

variable "ns_record_ttl" {
  default = 172800
  type    = number
}

variable "ns_record_allow_overwrite" {
  default = true
  type    = bool
}

variable "nameservers" {
  default = [
    "ns-382.awsdns-47.com.",
    "ns-875.awsdns-45.net.",
    "ns-1176.awsdns-19.org.",
    "ns-1880.awsdns-43.co.uk."
  ]
  type = list(string)
}

##### TXT Record #####

variable "with_txt_record" {
  default = false
  type    = bool
}

variable "txt_record_values" {
  default = [
    "v=spf1",
    "include:spf.protection.outlook.com -all",
    "MS=ms18260796"
  ]
  type = list(string)
}

variable "txt_record_ttl" {
  default = 3600
  type    = number
}

##### SOA Record #####

variable "with_soa_record" {
  default = false
  type    = bool
}

variable "soa_record_ttl" {
  default = 900
  type    = number
}

variable "soa_record_allow_overwrite" {
  default = true
  type    = bool
}

variable "soa_record_values" {
  default = [
    "ns-1247.awsdns-27.org. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"
  ]
  type = list(string)
}

##### MX Record #####

variable "with_mx_record" {
  default = false
  type    = bool
}

variable "mx_record_ttl" {
  default = 3600
  type    = number
}

variable "mx_record_allow_overwrite" {
  default = true
  type    = bool
}

variable "mx_record_values" {
  default = [
    "10 aspmx.l.google.com",
    "20 alt1.aspmx.l.google.com",
    "30 alt2.aspmx.l.google.com",
    "40 alt3.aspmx.l.google.com",
    "50 alt4.aspmx.l.google.com"
  ]
  type = list(string)
}

##### Records #####

variable "weighted_record" {
  default = {
    record1 = {
      record_name            = "w.redkube.cloud"
      record_type            = "A"
      record_ttl             = 300
      record_allow_overwrite = true
      record_values          = ["3.227.247.127"]
      set_identifier         = "nginx"
      weight                 = 10
    }
    record2 = {
      record_name            = "w.redkube.cloud"
      record_type            = "A"
      record_ttl             = 300
      record_allow_overwrite = true
      record_values          = ["107.23.70.244"]
      set_identifier         = "apache"
      weight                 = 90
    }
  }
}

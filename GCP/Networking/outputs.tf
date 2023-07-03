output "network" {
  value = module.gcp-network.network_name
}

output "gke_ip_range_pods_name" {
  value = var.gke_ip_range_pods_name
}

output "gke_ip_range_services_name" {
  value = var.gke_ip_range_services_name
}

output "ip_cidr_range_services" {
  value = var.ip_cidr_range_services
}

output "ip_cidr_range_pods" {
  value = var.ip_cidr_range_pods
}

output "subnet_ip_cidr" {
  value = var.subnet_ip_cidr
}

output "subnetwork" {
  value = var.subnetwork
}
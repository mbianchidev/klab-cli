module "gcp-network" {
  source       = "terraform-google-modules/network/google"
  project_id   = var.project
  network_name = var.network

  subnets = [
    {
      subnet_name   = var.subnetwork
      subnet_ip     = var.subnet_ip_cidr
      subnet_region = var.region
    },
  ]

  secondary_ranges = {
    "${var.subnetwork}" = [
      {
        range_name    = var.gke_ip_range_pods_name
        ip_cidr_range = var.ip_cidr_range_pods
      },
      {
        range_name    = var.gke_ip_range_services_name
        ip_cidr_range = var.ip_cidr_range_services
      }
    ]
  }
}

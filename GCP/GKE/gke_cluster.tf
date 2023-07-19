module "gke" {
  source                     = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  project_id                 = var.project_id
  name                       = "${var.cluster_name}-${var.env_name}"
  regional                   = var.gke_regional
  region                     = var.region
  zones                      = var.gke_zones
  network                    = module.gcp-network.network_name
  subnetwork                 = module.gcp-network.subnets_names[0]
  ip_range_pods              = var.gke_ip_range_pods_name
  ip_range_services          = var.gke_ip_range_services_name
  horizontal_pod_autoscaling = var.gke_horizontal_pod_autoscaling

  node_pools = [
    {
      name         = var.node_pool_name
      machine_type = var.node_pool_machine_type
      min_count    = var.node_pool_min_count
      max_count    = var.node_pool_max_count
      disk_size_gb = var.node_pool_disksize
      preemptible  = var.node_pool_preemptible
      auto_repair  = var.node_pool_auto_repair
      auto_upgrade = var.node_pool_auto_upgrade
      autoscaling  = var.node_pool_autoscaling
    },
  ]
}

output "cluster_name" {
  description = "Cluster name"
  value       = module.gke.name
}

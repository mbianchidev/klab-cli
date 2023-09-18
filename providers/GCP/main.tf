provider "google" {
  credentials = file("../kubelab-cli/credentials/gcp_kube_credential")
  project     = module.gke_module.project_id
  region      = module.gke_module.region
}

module "gke_module" {
  source       = "./GKE"
  cluster_name = var.cluster_name
  project      = var.project
  region       = var.region
  gke_zones    = ["${var.region}-a", "${var.region}-b", "${var.region}-c"]
}

output "cluster_name" {
  value = module.gke_module.cluster_name
}

output "cluster_project" {
  value = module.gke_module.project_id
}

output "cluster_region" {
  value = module.gke_module.region
}

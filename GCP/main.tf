provider "google" {
  credentials = file("../kubelab-cli/credentials/gcp_kube_credential.json")
  project     = module.gke_module.project_id
  region      = module.gke_module.region
}

module "gke_module" {
  source       = "./GKE"
  cluster_name = "gke-terraform"
  project_id   = "cts-project-388707"
  region       = "us-central1"
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

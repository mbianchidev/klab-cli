provider "google" {
  credentials = file("../kubelab-cli/credentials/gcp_kube_credential.json")
  project     = module.gke_module.project_id
  region      = module.gke_module.region
}

module "gke_module" {
  source     = "./GKE"
}

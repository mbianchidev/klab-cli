provider "google" {
  credentials = file("../kubelab-cli/credentials/gcp_kube_credential.json")
  project     = module.GKE.project_id
  region      = module.GKE.region
}

module "gcp-network" {
  source     = "./Networking"
  region     = module.GKE.region
  project_id = module.GKE.project_id
}

module "GKE" {
  source                     = "./GKE"
  gke_ip_range_pods_name     = module.gcp-network.gke_ip_range_pods_name
  network                    = module.gcp-network.network
  subnetwork                 = module.gcp-network.subnetwork
  subnet_ip_cidr             = module.gcp-network.subnet_ip_cidr
  gke_ip_range_services_name = module.gcp-network.gke_ip_range_services_name
  ip_cidr_range_services     = module.gcp-network.ip_cidr_range_services
  ip_cidr_range_pods         = module.gcp-network.ip_cidr_range_pods
}

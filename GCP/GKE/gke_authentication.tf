module "gke_auth" {
  source       = "terraform-google-modules/kubernetes-engine/google//modules/auth"
  project_id   = var.project_id
  location     = module.gke.location
  cluster_name = module.gke.name

  depends_on = [module.gke]
}

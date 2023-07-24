# provider "aws" {
#   shared_credentials_files = ["../kubelab-cli/credentials/aws_kube_credential"]
#   region = file("../kubelab-cli/credentials/aws_kube_config")
# }

# module "CodePipeline" {
#   source = "./CodePipeline"
#   github_oauth_token = "Your GitHub oauth token"
# }
# module "API-Gateway" {
#   source = "./API-Gateway"
# }
# module "Route53" {
#   source = "./Route53"
# }
# module "EBS" {
#   source = "./EBS"
# }
# module "S3" {
#   source = "./S3"
#  }
module "VPC" {
  source = "./VPC"
}
module "EKS" {
  source = "./EKS"
  vpc_public_subnet_1 = values(module.VPC.public_id)
  vpc_private_subnet_1 = values(module.VPC.private_id)
  vpc_security_group = module.VPC.security_group_id
}

# output "ebs_ids" {
#   value = module.EBS.ebs_id
# }
# output "api_gateway_url" {
#   value = module.API-Gateway.api_gateway_url
# }

# output "cluster_name" {
#   value = module.EKS.cluster_name
# }

# output "cluster_region" {
#   value = file("../kubelab-cli/credentials/aws_kube_config")
# }
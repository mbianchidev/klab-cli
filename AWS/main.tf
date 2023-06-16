module "CodePipeline" {
  source = "./CodePipeline"
  github_oauth_token = "Your GitHub oauth token"
}
module "API-Gateway" {
  source = "./API-Gateway"
}
module "Route53" {
  source = "./Route53"
}
module "EBS" {
  source = "./EBS"
}
module "S3" {
  source = "./S3"
 }
module "VPC" {
  source = "./VPC"
}
module "EKS" {
  source = "./EKS"
  vpc_public_subnet_1 = values(module.VPC.public_id)
  vpc_private_subnet_1 = values(module.VPC.private_id)
  vpc_security_group = module.VPC.security_group_id
}

output "ebs_ids" {
  value = module.EBS.ebs_id
}
output "api_gateway_url" {
  value = module.API-Gateway.api_gateway_url
}
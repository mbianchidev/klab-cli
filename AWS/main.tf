module "API-Gateway" {
  source = "./API-Gateway"
}
# module "EBS" {
#   source = "./EBS"
# }

# module "S3" {
#   source = "./S3"
  
# # }
# module "VPC" {
#   source = "./VPC"
# }
# module "EKS" {
#   source = "./EKS"
#   vpc_public_subnet_1 = values(module.VPC.public_id)
#   vpc_private_subnet_1 = values(module.VPC.private_id)
#   vpc_security_group = module.VPC.security_group_id
# }
# output "subnet_public" {
#   value = module.VPC.public_id
# }
# output "subnet_private" {
#   value = module.VPC.private_id
# }
# output "security_group_id" {
#   value = module.VPC.security_group_id
# }
# output "ebs_ids" {
#   value = module.EBS.ebs_id
# }
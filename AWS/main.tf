module "EBS" {
  source = "./EBS"
}

module "S3" {
  source = "./S3"
  
}
output "ebs_ids" {
  value = module.EBS.ebs_id
}
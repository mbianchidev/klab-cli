
resource "aws_ebs_volume" "example" {
  for_each = var.ebs_volume
  availability_zone = each.value.availability_zone
  encrypted         = each.value.encrypted
  size              = each.value.size
  type              = each.value.type

  tags = {
    Name = "ebs_for_eks"
  }
}
output "ebs_id" {
  value = { for k, v in aws_ebs_volume.example : k => v.id }
}

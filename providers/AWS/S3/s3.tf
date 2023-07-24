
resource "aws_s3_bucket" "example_bucket_1" {
  for_each = var.s3_bucket
  bucket = each.value.bucket
  force_destroy = each.value.force_destroy
  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
resource "aws_s3_bucket_versioning" "versioning_example_bucket_1" {
  for_each = var.s3_bucket
  bucket = aws_s3_bucket.example_bucket_1[each.key].id
  versioning_configuration {
    status = each.value.versioning_configuration
  }
}


variable "s3_bucket" {
  description = "Variables for creating S3 dinamicly"
  default = {
    s3_first = {
      force_destroy = true
      bucket = "kubelab-bucket"
      versioning_configuration = "Enabled"
    }
    s3_second = {
      force_destroy = true
      bucket = "blagoj-bucket"
      versioning_configuration = "Enabled"
    }
  }
}


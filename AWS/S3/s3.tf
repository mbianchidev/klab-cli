{%- for bucket in buckets%}
resource "aws_s3_bucket" "example_{{bucket.bucket_resource_name}}" {
  bucket = "{{bucket.bucket_name}}"
  force_destroy = {{bucket.force_destroy | lower}}
  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
{%- if bucket.object_ownership %}
resource "aws_s3_bucket_ownership_controls" "example_{{bucket.bucket_resource_name}}" {
  bucket = aws_s3_bucket.example_{{bucket.bucket_resource_name}}.id
  rule {
    object_ownership = "{{bucket.object_ownership}}"
  }
}
{%- endif %}
{%- if bucket.acl %}
resource "aws_s3_bucket_acl" "acl_example_{{bucket.bucket_resource_name}}" {
  depends_on = [aws_s3_bucket_ownership_controls.example_{{bucket.bucket_resource_name}}]
  bucket = aws_s3_bucket.example_{{bucket.bucket_resource_name}}.id
  acl    = "{{bucket.acl}}"
}
{%- endif %}
{%- if bucket.public_access_block %}
resource "aws_s3_bucket_public_access_block" "example_{{bucket.bucket_resource_name}}" {
  bucket = aws_s3_bucket.example_{{bucket.bucket_resource_name}}.id

  block_public_acls       = {{bucket.block_public_acls | lower}}
  block_public_policy     = {{bucket.block_public_policy | lower}}
  ignore_public_acls      = {{bucket.ignore_public_acls | lower}}
  restrict_public_buckets = {{bucket.restrict_public_buckets | lower}}
}
{%- endif %}
{%- if bucket.versioning_configuration %}
resource "aws_s3_bucket_versioning" "versioning_example_{{bucket.bucket_resource_name}}" {
  bucket = aws_s3_bucket.example_{{bucket.bucket_resource_name}}.id
  versioning_configuration {
    status = "{{bucket.versioning_configuration}}"
  }
}
{%- endif %}
{%- if bucket.allow_access_from_another_account %}
resource "aws_s3_bucket_policy" "allow_access_from_another_account_{{bucket.bucket_resource_name}}" {
  bucket = aws_s3_bucket.example_{{bucket.bucket_resource_name}}.id
  policy = data.aws_iam_policy_document.allow_access_from_another_account.json
}

data "aws_iam_policy_document" "allow_access_from_another_account" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["{{bucket.identifiers}}"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.example_{{bucket.bucket_resource_name}}.arn,
      "${aws_s3_bucket.example_{{bucket.bucket_resource_name}}.arn}/*",
    ]
  }
}
{%- endif %}
{%- if bucket.obejct_key %}
resource "aws_s3_object" "object_{{loop.index}}" {
  bucket = "example_{{bucket.bucket_resource_name}}"
  key    = "{{bucket.obejct_key}}"
  # source = "path/to/file"

  # The filemd5() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
  # etag = "${md5(file("path/to/file"))}"
  etag = filemd5("path/to/file")
}
{%- endif %}


{% endfor%}
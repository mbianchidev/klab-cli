provider "aws" {
  region = var.region
}
variable "region" {
  type = string
  description = "Region in which you like to deploy the CodePipeline"
  default = "eu-west-1"
}
resource "aws_s3_bucket" "codepipeline_bucket_{{region}}" {
  
  force_destroy = true
}
resource "aws_s3_bucket" "codebuild_artifacts" {
  bucket_prefix = "{{codebuild_artifacts_prefix}}"
  force_destroy = true 
}
resource "aws_codebuild_project" "terraform_plan_{{region}}" {
  name          = "code_build_terraform_plan"
  description   = "codebuild_project_plan"
  build_timeout = "15"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  cache {
    type     = "S3"
    location = aws_s3_bucket.codebuild_artifacts.bucket
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "log-group"
      stream_name = "log-stream"
    }

    s3_logs {
      status   = "ENABLED"
      location = "${aws_s3_bucket.codebuild_artifacts.bucket}/build-log"
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "Modules/Terraform/conf/Environments/{{environment}}/buildspec_${var.region}.yml"
  }
}
resource "aws_codepipeline" "code_pipeline" {
  name = "{{pipeline_name}}"

  artifact_store {
    location = aws_s3_bucket.codepipeline_bucket_{{region}}.bucket
    type     = "S3"
  }
  role_arn = aws_iam_role.codepipeline_role.arn

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        Owner     = "{{owner}}"
        Repo      = "{{repo_name}}"
        Branch    = "{{branch_name}}"
        OAuthToken = "{{oauth_tocken}}"
      }
    }
  }
  stage {
    name = "Build"

    action {
      name             = "Build-{{region}}"
      region           = "eu-west-1"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output-{{region}}"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.terraform_plan_{{region}}.name
      }
    }
  }

  
}

# IAM Roles
resource "aws_iam_role" "codebuild_role" {
  name = "CodeBuild-Role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "codebuild_policy" {
  name        = "CodeBuild-Policy"
  description = "Policy for CodeBuild to deploy to EKS"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "*:*",
        "eks:List*",
        "eks:Create*",
        "eks:Delete*",
        "eks:Update*",
        "ec2:*",
        "ec2:List*",
        "ecr:GetAuthorizationToken",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:CreateRepository",
        "ecr:ListImages",
        "ecr:DescribeRepositories",
        "ecr:DeleteRepository",
        "ecr:DeleteRepositoryPolicy",
        "ecr:SetRepositoryPolicy",
        "ecr:GetRepositoryPolicy",
        "ecr:TagResource",
        "ecr:UntagResource",
        "ecr:DescribeImages",
        "iam:PassRole",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "codebuild_policy_attachment" {
  role       = aws_iam_role.codebuild_role.name
  policy_arn = aws_iam_policy.codebuild_policy.arn
}

resource "aws_iam_role" "codepipeline_role" {
  name = "codepipeline-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "codepipeline_policy"
  role = aws_iam_role.codepipeline_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action": [
        "s3:*",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:*",
        "codebuild:StartBuild"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}
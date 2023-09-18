# EKS cluster role 

resource "aws_iam_role" "eks_cluster_role" {
  name               = "eks_cluster_role"
  assume_role_policy = file("${path.module}/cluster_assume_policy.json")
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS node groups roles

resource "aws_iam_role" "eks_general_node_group_role" {
  name               = "managed_node_role"
  assume_role_policy = file("${path.module}/node_group_assume_policy.json")
}

resource "aws_iam_policy" "efs_policy" {
  name        = "eks_efs_policy"
  description = "Policy for EFS access"
  policy      = file("${path.module}/node_group_efs_policy.json")
}

resource "aws_iam_role_policy_attachment" "efs_policy_attachment" {
  policy_arn = aws_iam_policy.efs_policy.arn
  role       = aws_iam_role.eks_general_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy_general" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_general_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy_general_cloudwatch" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.eks_general_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy_general" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_general_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry_read_only" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_general_node_group_role.name
}

# EKS cluster and node groups

resource "aws_eks_cluster" "eks" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    endpoint_private_access = var.endpoint_private_access
    endpoint_public_access  = var.endpoint_public_access

    subnet_ids = concat(
      [for subnet_id in var.vpc_public_subnet_1 : subnet_id],
      [for subnet_id in var.vpc_private_subnet_1 : subnet_id]
    )
  }
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

# resource "null_resource" "update_aws_auth1" {
#   provisioner "local-exec" {
#     command = <<EOT
#       eksctl create iamidentitymapping \
#         --cluster eks \
#         --region eu-west-1 \
#         --arn arn:aws:iam::530833340881:user/Daniel \
#         --group system:masters \
#         --no-duplicate-arns \
#         --username daniel      
#         EOT
#   }
#   depends_on = [ 
#     aws_eks_cluster.eks, 
#     aws_eks_node_group.eks_general_node_group_1    
#     ]
# }

resource "aws_eks_node_group" "eks_general_node_group_1" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "node-general_1_group_1"
  node_role_arn   = aws_iam_role.eks_general_node_group_role.arn
  subnet_ids      = var.vpc_private_subnet_1

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 1
  }

  ami_type             = var.ami_type
  capacity_type        = var.capacity_type
  disk_size            = var.disk_size
  force_update_version = false
  instance_types       = [var.instance_type]

  labels = {
    role = "node-general-1"
  }
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy_general,
    aws_iam_role_policy_attachment.eks_cni_policy_general,
    aws_iam_role_policy_attachment.ec2_container_registry_read_only,
    aws_iam_role_policy_attachment.efs_policy_attachment
  ]
}

# output "efs_id" {
#   value = aws_efs_file_system.eks_efs_file_system.id
# }

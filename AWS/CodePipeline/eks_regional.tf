
# Network 

resource "aws_vpc" "eks_vpc" {
  cidr_block                       = "192.168.0.0/16"
  instance_tenancy                 = "default"
  enable_dns_support               = true
  enable_dns_hostnames             = true
  tags = {
    Name = "test-eks-vpc"
    Environment = "dev"
  }
}

###### Public #####
resource "aws_subnet" "eks_public_subnet_1" {
  vpc_id                  = aws_vpc.eks_vpc.id
  cidr_block              = "192.168.0.0/18"
  availability_zone       = "eu-west-1a"
  map_public_ip_on_launch = true
  tags = {
        "Name" = "public-eu-west-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/elb" = "1"
  }
}
resource "aws_route_table_association" "route_table_association_public_subnet_1" {
  subnet_id      = aws_subnet.eks_public_subnet_1.id
  route_table_id = aws_route_table.eks_public_route_table.id
}
resource "aws_nat_gateway" "eks_nat_gateway_subnet_1" {
  allocation_id = aws_eip.eks_nat_gateway_elastic_ip_subnet_1.id
  subnet_id     = aws_subnet.eks_public_subnet_1.id
  tags          = {
        Name = "EKS NAT 1"
  }
}
resource "aws_eip" "eks_nat_gateway_elastic_ip_subnet_1" {
  depends_on = [
    aws_internet_gateway.eks_internet_gateway
  ]
}
resource "aws_subnet" "eks_public_subnet_2" {
  vpc_id                  = aws_vpc.eks_vpc.id
  cidr_block              = "192.168.64.0/18"
  availability_zone       = "eu-west-1b"
  map_public_ip_on_launch = true
  tags = {
        "Name" = "public-eu-west-1b"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/elb" = "1"
  }
}
resource "aws_route_table_association" "route_table_association_public_subnet_2" {
  subnet_id      = aws_subnet.eks_public_subnet_2.id
  route_table_id = aws_route_table.eks_public_route_table.id
}
resource "aws_nat_gateway" "eks_nat_gateway_subnet_2" {
  allocation_id = aws_eip.eks_nat_gateway_elastic_ip_subnet_2.id
  subnet_id     = aws_subnet.eks_public_subnet_2.id
  tags          = {
        Name = "EKS NAT 2"
  }
}
resource "aws_eip" "eks_nat_gateway_elastic_ip_subnet_2" {
  depends_on = [
    aws_internet_gateway.eks_internet_gateway
  ]
}

resource "aws_route_table" "eks_public_route_table" {
  vpc_id = aws_vpc.eks_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks_internet_gateway.id
  }
}


resource "aws_internet_gateway" "eks_internet_gateway" {
  vpc_id = aws_vpc.eks_vpc.id

  tags = {
        Name = "EKS Internet Gateway"
  }
}
### Private ###
resource "aws_subnet" "eks_private_subnet_1" {
  vpc_id            = aws_vpc.eks_vpc.id
  cidr_block        = "192.168.128.0/18"
  availability_zone = "eu-west-1a"
  tags = {
        "Name" = "private-eu-west-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/internal-elb" = "1"
  }
}
resource "aws_route_table_association" "route_table_association_private_subnet_1" {
  subnet_id      = aws_subnet.eks_private_subnet_1.id
  route_table_id = aws_route_table.eks_private_route_table_subnet_1.id
}
resource "aws_route_table" "eks_private_route_table_subnet_1" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.eks_nat_gateway_subnet_1.id
  }

  tags = {
        "Name" = "private-eu-west-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/internal-elb" = "1"
  }
}
resource "aws_subnet" "eks_private_subnet_2" {
  vpc_id            = aws_vpc.eks_vpc.id
  cidr_block        = "192.168.192.0/18"
  availability_zone = "eu-west-1b"
  tags = {
        "Name" = "private-eu-west-1b"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/internal-elb" = "1"
  }
}
resource "aws_route_table_association" "route_table_association_private_subnet_2" {
  subnet_id      = aws_subnet.eks_private_subnet_2.id
  route_table_id = aws_route_table.eks_private_route_table_subnet_2.id
}
resource "aws_route_table" "eks_private_route_table_subnet_2" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.eks_nat_gateway_subnet_2.id
  }

  tags = {
        "Name" = "private-eu-west-1b"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/internal-elb" = "1"
  }
}
resource "aws_security_group" "eks_security_group" {
  name        = "eks-sg"
  vpc_id      = aws_vpc.eks_vpc.id
  ingress {
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = ["192.168.0.0/16"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0","192.168.2.0/24"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
        Name = "eks-efs"
  }
  depends_on = [
    aws_vpc.eks_vpc
  ]
}
# File system

resource "aws_efs_file_system" "eks_efs_file_system" {
  performance_mode = "generalPurpose"
  encrypted        = true
}
resource "aws_efs_mount_target" "efs_mount_target_1" {
  file_system_id  = aws_efs_file_system.eks_efs_file_system.id
  subnet_id       = aws_subnet.eks_private_subnet_1.id
  security_groups = [aws_security_group.eks_security_group.id]

  depends_on = [
    aws_subnet.eks_private_subnet_1
  ]
}
resource "aws_efs_mount_target" "efs_mount_target_2" {
  file_system_id  = aws_efs_file_system.eks_efs_file_system.id
  subnet_id       = aws_subnet.eks_private_subnet_2.id
  security_groups = [aws_security_group.eks_security_group.id]

  depends_on = [
    aws_subnet.eks_private_subnet_2
  ]
}
# EKS cluster role 

resource "aws_iam_role" "eks_cluster_role" {
  name               = "eks_cluster_role"
  assume_role_policy = "${file("${path.module}/../../Modules/Terraform/templates/EKS/cluster_assume_policy.json")}"
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS node groups roles

resource "aws_iam_role" "eks_general_node_group_role" {
  name               = "managed_node_role"
  assume_role_policy = "${file("${path.module}/../../Modules/Terraform/templates/EKS/node_group_assume_policy.json")}" 
}

resource "aws_iam_policy" "efs_policy" {
  name        = "eks_efs_policy"
  description = "Policy for EFS access"
  policy      = "${file("${path.module}/../../Modules/Terraform/templates/EKS/node_group_efs_policy.json")}"
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
  name     = "eks"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    endpoint_private_access = false
    endpoint_public_access  = true
    
    subnet_ids = [
      aws_subnet.eks_public_subnet_1.id,
      aws_subnet.eks_public_subnet_2.id,
      aws_subnet.eks_private_subnet_1.id,
      aws_subnet.eks_private_subnet_2.id,
    ]
    
  } 
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

resource "null_resource" "update_aws_auth1" {
  provisioner "local-exec" {
    command = <<EOT
      eksctl create iamidentitymapping \
        --cluster eks \
        --region eu-west-1 \
        --arn None \
        --group system:masters \
        --no-duplicate-arns \
        --username daniel      
        EOT
  }
  depends_on = [ 
    aws_eks_cluster.eks, 
    aws_eks_node_group.eks_general_node_group_1    
    ]
}
resource "aws_eks_node_group" "eks_general_node_group_1" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "node-general_1_group_1"
  node_role_arn   = aws_iam_role.eks_general_node_group_role.arn

  
    subnet_ids = [
      aws_subnet.eks_private_subnet_1.id,
      aws_subnet.eks_private_subnet_2.id,
    ]
    

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 1
  }

  ami_type             = "AL2_x86_64"
  capacity_type        = "ON_DEMAND"
  disk_size            = 20
  force_update_version = false
  instance_types       = ["t3.medium"]

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
output "efs_id" {
  value = aws_efs_file_system.eks_efs_file_system.id
}

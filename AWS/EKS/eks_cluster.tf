{%- if vpc %}
# Network 

resource "aws_vpc" "eks_vpc" {
  cidr_block                       = "{{eks_vpc_cidr_block}}"
  instance_tenancy                 = "{{eks_vpc_instance_tenancy | lower}}"
  enable_dns_support               = {{eks_vpc_enable_dns_support | lower}}
  enable_dns_hostnames             = {{eks_vpc_enable_dns_hostnames | lower}}
  tags = {
    {%- for k,v in vpc_tags.items() %}
    {{ k }} = "{{ v }}"
    {%- endfor %}
  }
}

###### Public #####
{%- for k,v in subnets_public.items() %}
resource "aws_subnet" "eks_public_{{k}}" {
  vpc_id                  = aws_vpc.eks_vpc.id
  cidr_block              = "{{v.cidr_block}}"
  availability_zone       = "{{v.availability_zone}}"
  map_public_ip_on_launch = {{v.map_public_ip_on_launch | lower}}
  tags = {
     "Name" = "public-{{region}}"
     "kubernetes.io/cluster/{{eks_cluster_name}}" = "shared"
    {%- for t,k in v.tags.items() %}
        "{{t}}" = "{{k}}"
    {%- endfor %}
  }
}
resource "aws_route_table_association" "route_table_association_public_{{k}}" {
  subnet_id      = aws_subnet.eks_public_{{k}}.id
  route_table_id = aws_route_table.eks_public_route_table.id
}
resource "aws_nat_gateway" "eks_nat_gateway_{{k}}" {
  allocation_id = aws_eip.eks_nat_gateway_elastic_ip_{{k}}.id
  subnet_id     = aws_subnet.eks_public_{{k}}.id
  tags          = {
    {%- for t,k in v.tags_nat_gateway.items() %}
        {{t}} = "{{k}}"
    {%- endfor %}
  }
}
resource "aws_eip" "eks_nat_gateway_elastic_ip_{{k}}" {
  depends_on = [
    aws_internet_gateway.eks_internet_gateway
  ]
}
{%- endfor %}

resource "aws_route_table" "eks_public_route_table" {
  vpc_id = aws_vpc.eks_vpc.id
  route {
    cidr_block = "{{public_route_table_cidr_block}}"
    gateway_id = aws_internet_gateway.eks_internet_gateway.id
  }
}


resource "aws_internet_gateway" "eks_internet_gateway" {
  vpc_id = aws_vpc.eks_vpc.id

  tags = {
    {%- for t,k in internet_gateway_tags.items() %}
        {{t}} = "{{k}}"
    {%- endfor %}
  }
}
### Private ###
{%- for k,v in subnets_private.items() %}
resource "aws_subnet" "eks_private_{{k}}" {
  vpc_id            = aws_vpc.eks_vpc.id
  cidr_block        = "{{v.cidr_block}}"
  availability_zone = "{{v.availability_zone}}"
  tags = {
     "Name" = "private-{{region}}"
     "kubernetes.io/cluster/{{eks_cluster_name}}" = "shared"
    {%- for t,k in v.tags.items() %}
        "{{t}}" = "{{k}}"
    {%- endfor %}
  }
}
resource "aws_route_table_association" "route_table_association_private_{{k}}" {
  subnet_id      = aws_subnet.eks_private_{{k}}.id
  route_table_id = aws_route_table.eks_private_route_table_{{k}}.id
}
resource "aws_route_table" "eks_private_route_table_{{k}}" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block     = "{{v.route_table_cidr_block}}"
    nat_gateway_id = aws_nat_gateway.eks_nat_gateway_{{v.for_nat_gateway_public}}.id
  }

  tags = {
    {%- for t,k in v.tags.items() %}
        "{{t}}" = "{{k}}"
    {%- endfor %}
  }
}

{%- endfor %}
resource "aws_security_group" "eks_security_group" {
  name        = "{{sg_name_prefix}}"
  vpc_id      = aws_vpc.eks_vpc.id
{%- for k,v in ingress.items() %}
  ingress {
    from_port   = {{ v.from_port }}
    to_port     = {{ v.to_port }}
    protocol    = "{{v.protocol}}"
    cidr_blocks = {{v.cidr_blocks | safe}}
  }
  {%- endfor %}
  {%- for j,e in egress.items() %}
  egress {
    from_port   = {{e.from_port}}
    to_port     = {{e.to_port}}
    protocol    = "{{e.protocol}}"
    cidr_blocks = {{ e.cidr_blocks | safe}}
    ipv6_cidr_blocks = ["{{e.ipv6_cidr_blocks}}"]
  }
{%- endfor %}

  tags = {
    {%- for t,k in sg_tags.items() %}
        {{t}} = "{{k}}"
    {%- endfor %}
  }
  depends_on = [
    aws_vpc.eks_vpc
  ]
}
{%- else %}
variable "vpc_public_subnet_1" {
  description = "Public Subnet ID for EKS"
  type        = string
}
variable "vpc_public_subnet_2" {
  description = "Public Subnet ID for EKS"
  type        = string
}
variable "vpc_private_subnet_1" {
  description = "Private Subnet ID for EKS"
  type        = string
}
variable "vpc_private_subnet_2" {
  description = "Private Subnet ID for EKS"
  type        = string
}
variable "vpc_security_group" {
  description = "security_group ID for EKS"
  type        = string
}
{%- endif%}

{%- if efs_file_system %}
# File system

resource "aws_efs_file_system" "eks_efs_file_system" {
  performance_mode = "{{efs_file_system_performance_mode}}"
  encrypted        = {{efs_file_system_encrypted | lower}}
}
{%- if vpc %}
 {%- for k in efs_mount_target %}
resource "aws_efs_mount_target" "efs_mount_{{k.mount_target}}" {
  file_system_id  = aws_efs_file_system.eks_efs_file_system.id
  subnet_id       = aws_subnet.eks_private_{{k.for_private_subnet}}.id
  security_groups = [aws_security_group.eks_security_group.id]

  depends_on = [
    aws_subnet.eks_private_{{k.for_private_subnet}}
  ]
}
 {%- endfor %}
{%- else  %}
{%- for s in external_subnets_private%}
resource "aws_efs_mount_target" "efs_mount_target_{{loop.index}}" {
  file_system_id  = aws_efs_file_system.eks_efs_file_system.id
  subnet_id       = {{s}}
  security_groups = [var.vpc_security_group]

} 
{%- endfor %}
{%-endif %}
{%-endif %}
# EKS cluster role 

resource "aws_iam_role" "eks_cluster_role" {
  name               = "eks_cluster_role"
  assume_role_policy = "${file("${path.module}/../templates/EKS/cluster_assume_policy.json")}"
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS node groups roles

resource "aws_iam_role" "eks_general_node_group_role" {
  name               = "managed_node_role"
  assume_role_policy = "${file("${path.module}/../templates/EKS/node_group_assume_policy.json")}" 
}

resource "aws_iam_policy" "efs_policy" {
  name        = "eks_efs_policy"
  description = "Policy for EFS access"
  policy      = "${file("${path.module}/../templates/EKS/node_group_efs_policy.json")}"
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
  name     = "{{eks_cluster_name}}"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    endpoint_private_access = {{eks_endpoint_private_access | lower}}
    endpoint_public_access  = {{eks_endpoint_public_access | lower}}
    {% if vpc %}
    subnet_ids = [
      {%- for s in subnets_public%}
      aws_subnet.eks_public_{{s}}.id,     
      {%- endfor%}
      {%- for s in subnets_private%}
      aws_subnet.eks_private_{{s}}.id,     
      {%- endfor%}
    ]
    {% else %}
    subnet_ids = [
        {%- for s in external_subnets_public%}
      {{s}},     
      {%- endfor%}
      {%- for s in external_subnets_private%}
      {{s}},     
      {%- endfor%}
      ]
    {% endif %}
  } 
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}
{% for a in auth_user%}
resource "null_resource" "update_aws_auth{{loop.index}}" {
  provisioner "local-exec" {
    command = <<EOT
      eksctl create iamidentitymapping \
        --cluster {{eks_cluster_name}} \
        --region {{a.region}} \
        --arn {{a.arn}} \
        --group system:masters \
        --no-duplicate-arns \
        --username {{a.username}}      
        EOT
  }
  depends_on = [ 
    aws_eks_cluster.eks,
    {%- if managed_nodes == true %}
    {%- for s in node_groups %} 
    aws_eks_node_group.eks_general_node_{{s}} 
    {%- endfor%}
    {%- endif %}    
    ]
}
{%- endfor%}
{%- if managed_nodes == true %}
{%- for s,v in node_groups.items() %}
resource "aws_eks_node_group" "eks_general_node_{{s}}" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "{{v.node_group_name}}_{{s}}"
  node_role_arn   = aws_iam_role.eks_general_node_group_role.arn

  {% if vpc %}
    subnet_ids = [
      {%- for s in subnets_private%}
      aws_subnet.eks_private_{{s}}.id,     
      {%- endfor%}
    ]
    {% else %}
    subnet_ids = [
      {%- for s in external_subnets_private%}
      {{s}},     
        {%- endfor%}
      ]
    {% endif %}

  scaling_config {
    desired_size = {{v.node_group_desired_size}}
    max_size     = {{v.node_group_max_size}}
    min_size     = {{v.node_group_min_size}}
  }

  ami_type             = "{{v.node_group_ami_type}}"
  capacity_type        = "{{v.node_group_capacity_type}}"
  disk_size            = {{v.node_group_disk_size}}
  force_update_version = {{v.node_group_force_update_version | lower}}
  instance_types       = ["{{v.node_group_instance_type}}"]

  labels = {
    role = "{{v.node_group_role_label}}"
  }
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy_general,
    aws_iam_role_policy_attachment.eks_cni_policy_general,
    aws_iam_role_policy_attachment.ec2_container_registry_read_only,
    aws_iam_role_policy_attachment.efs_policy_attachment
  ]
}
{%- endfor%}
{%- endif %}


{%- if efs_file_system %}
output "efs_id" {
  value = aws_efs_file_system.eks_efs_file_system.id
}
{%- endif %}

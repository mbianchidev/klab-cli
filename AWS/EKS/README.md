# Infinity Gauntlet

## Company Name: KubeLab

### Author: Blagoj Vazliski
### Creation Date: 2023-05-19
### Last Updated: 2023-05-23


## About

This code sets up the network and resources required for an AWS Elastic Kubernetes Service (EKS) cluster or you can use it in your own vpc just with providing subnet_ids. It creates a VPC, subnets (public and private), route tables, NAT gateways, security groups, EFS file system, IAM roles, and an EKS cluster with a node group.

## Features
This code provides the following features:

 - Network Configuration: The code sets up a Virtual Private Cloud (VPC) on AWS with the specified CIDR block, DNS support, and DNS hostnames enabled. It creates public and private subnets in different availability zones, configures route tables, and associates them with the appropriate subnets. It also sets up NAT gateways and an internet gateway for outbound connectivity.

 - File System: The code provisions an Elastic File System (EFS) on AWS. It creates a file system with general-purpose performance mode and enables encryption. It also sets up mount targets in the private subnets, ensuring secure access to the file system from within the VPC.

 - EKS Cluster and Node Groups: The code creates an Amazon Elastic Kubernetes Service (EKS) cluster and node groups. It defines the cluster name and associates the necessary IAM roles for the cluster and node groups. The cluster is configured to have public endpoint access and private access within the VPC. The node groups are configured with desired scaling, instance types, and other parameters.

 - IAM Roles and Policies: The code creates IAM roles and policies required for the EKS cluster and node groups. It sets up the cluster role, which defines the permissions and policies associated with the EKS cluster. It also creates the node group role with attached policies such as AmazonEKSWorkerNodePolicy, CloudWatchAgentServerPolicy, AmazonEKS_CNI_Policy, and AmazonEC2ContainerRegistryReadOnly.
## Design

The provided code follows an Infrastructure-as-Code (IaC) approach using Terraform to provision and configure the required AWS resources for an EKS cluster and related network components

## Deployments Target(s)

The designed infrastructure targets users who want to set up an EKS cluster on AWS along with the associated networking components. It is suitable for DevOps engineers, system administrators, or developers who require a scalable and managed Kubernetes environment for deploying containerized applications.

## Dependencies
The code has the following dependencies:

  - Terraform AWS Provider: The code relies on the AWS provider for Terraform to interact with AWS services. Ensure that the provider is correctly configured in your Terraform environment.
  - The code assumes that all other necessary dependencies, such as Terraform itself and its dependencies, are already installed and properly set up.

  - Please note that the code may have additional dependencies based on the network you want to deploy, that means that if you want to deploy in your VPC you need to provide subnet_ids from that network.

## Known Limitations/TODOs
   * Currently only supports autosccaling for manged nodes


## Parameters
| Parameter                  |   Type   | Required | Default           | Description                                                                                                                                      |
|---------------------------|----------|----------|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| managed_nodes              |  String  |    ✅    | true              | Defines whether managed nodes should be used or not.                                                                                              |
| node_groups                |  String  |    ✅    | group_1           | The name of the resource for managed nodes.                                                                                                       |
| node_group_name            |  String  |    ✅    | node-general_1    | The name of the managed node group.                                                                                                               |
| node_group_desired_size    |  Number  |    ✅    | 1                 | The desired number of nodes in the node group.                                                                                                    |
| node_group_max_size        |  Number  |    ✅    | 3                 | The maximum number of nodes in the node group.                                                                                                    |
| node_group_min_size        |  Number  |    ✅    | 1                 | The minimum number of nodes in the node group.                                                                                                    |
| node_group_ami_type        |  String  |    ✅    | AL2_x86_64        | The AMI type for the node group.                                                                                                                  |
| node_group_capacity_type   |  String  |    ✅    | ON_DEMAND         | The capacity type for the node group.                                                                                                             |
| node_group_disk_size       |  Number  |    ✅    | 20                | The disk size in gigabytes for the nodes in the node group.                                                                                       |
| node_group_force_update_version | Boolean |  ✅    | false             | Specifies whether to force an update to the latest AMI version for the node group.                                                               |
| node_group_instance_type   |  String  |    ✅    | t3.medium         | The EC2 instance type for the nodes in the node group.                                                                                            |
| node_group_role_label      |  String  |    ✅    | node-general-1    | The role label for the nodes in the node group.                                                                                                   |
| node_group_subnets         |  Map     |    ✅    |                   | The subnets in which the nodes of the node group should be launched. Specify the subnet ID(s) or use variables for subnet references.             |
| eks_cluster_name           |  String  |   ✅     | eks               | The name of the EKS cluster.                                                                                                                     |
| eks_endpoint_private_access | Boolean |   ✅     | false             | Specifies whether the EKS cluster should have private endpoint access.                                                                            |
| eks_endpoint_public_access  | Boolean |   ✅     | true              | Specifies whether the EKS cluster should have public endpoint access.                                                                             |
| vpc                        | Boolean  |   ✅     | true              | Specifies whether a VPC should be created for the EKS cluster.                                                                                    |
| external_subnets_private   |  List    |   ✅     |                   | The private subnets for the VPC. Specify the subnet ID(s) or use variables for subnet references.                                                  |
| external_subnets_public    |  List    |   ✅     |                   | The public subnets for the VPC. Specify the subnet ID(s) or use variables for subnet references.                                                   |
| eks_vpc_cidr_block         |  String  |   ✅     | 192.168.0.0/16    | The CIDR block for the VPC.                                                                                                                       |
| eks_vpc_instance_tenancy   |  String  |   ✅     | default           | The tenancy option for instances launched in the VPC.                                                                                             |
| eks_vpc_enable_dns_support |  Boolean |   ✅    | true              | Specifies whether DNS resolution is supported for the VPC.                                                                                        |
| eks_vpc_enable_dns_hostnames | Boolean |  ✅    | true              | Specifies whether DNS hostnames are enabled for the VPC.                                                                                          |
| vpc_tags                   |  Map     |   ✅     | {"Name": "test-ecs-vpc", "Environment": "dev"} | Tags to be applied to the VPC.                                               |
| subnets_public             |  Map     |   ✅     |                   | Configuration for public subnets.                                                                                                                 |
| subnets_private            |  Map     |   ✅     |                   | Configuration for private subnets.                                                                                                                |
| efs_file_system            | Boolean  |   ✅     | true              | Specifies whether an EFS file system should be created.                                                                                           |
| efs_mount_target           |  List    |   ✅     |                   | Configuration for EFS mount targets.                                                                                                              |
| sg_name_prefix             |  String  |   ✅     | eks-sg            | The prefix for security group names.                                                                                                              |
| ingress                    |  Map     |   ✅     |                   | Configuration for ingress rules in security groups.                                                                                               |
| egress                     |  Map     |   ✅     |                   | Configuration for egress rules in security groups.                                                                                                |
| sg_tags                    |  Map     |   ✅     | {"Name": "eks-efs"} | Tags to be applied to the security groups.                                                                                                        |
| public_route_table_cidr_block | String |   ✅     | 0.0.0.0/0         | The CIDR block for the public route table.                                                                                                        |
| internet_gateway_tags      |  Map     |   ✅     | {"Name": "EKS Internet Gateway"} | Tags to be applied to the internet gateway.                              |




## License
No licenses needed

## Contributing
Thank you for your interest in contributing to this project! We welcome contributions from the community. To ensure a smooth collaboration, please follow these guidelines:

 - Fork the repository and clone it to your local machine.
 - Create a new branch for your contribution: git checkout -b my-feature.
 - Make your changes and test them thoroughly.
 - Ensure that your code adheres to the project's coding style and conventions.
 - Write clear and concise commit messages for your changes.
 - Push your branch to your forked repository: git push origin my-feature.
 - Submit a pull request to the main repository's develop branch.
 - Be prepared to address feedback and make necessary updates to your pull request.

Please note that all contributions will be reviewed by the project maintainers, and they may provide feedback or request modifications before merging your changes.

Thank you for your contributions and support in making this project better!
## Contact

Email: blagoj@kubelab.cloud


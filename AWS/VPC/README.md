## About
This module enables you to create a VPC with multiple subnets and security groups. With Ingress and Option for Nat Gateway too. It also enable to specify multiple Security Groups and routing tables. 

Features
Technical requirements

## Deployments Target(s)
Who ever requires a VPC with Internet Gateway or NatGateway with subnets and Security Group can use this module


Known Limitations/TODOs
Sometimes you can hit the limits of creating multiple VPC or Subnets. In this case you should increes the limit via AWS Support channels. 
 
Parameters
There are essentially five configurable options for the VPC module:

| Parameter               |  Type  | Required  | Default       | Description                                                                                                                                            |
|:------------------------|:------:|:---------:|:-------------:|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| vpc_cidr_block          | String | ✅        | 10.10.0.0/16  | VPC CIDR Block                                                                                                                                        |
| vpc_tags                | String | ❌        | {Name: "KubeLab"}             | Tags for VPC                                                                                                                         |
| nat_gateways            | List   | ❌        |               | Enabling NatGateway                                                                                                                                   |
| nat_gateway_name        | String | ❌        | ngw1, ngw2    | NatGateway Resource Name. You can have multiple                                                                                                       |
| for_subnet              | String | ❌        | Public1, Public2             | For which subnet is this NatGateway                                                                                                                   |
| route_tables            | List | ❌        |              | Routing Table configuration                                                                                                                           |
| rt_name                 | String | ❌        | rt1,rt2,rt3            | Name of the Routing table                                                                                                                             |
| rt_cidr_block           | String | ❌        | "0.0.0.0/0"             | Routing table CIDR Block                                                                                                                              |
| int_gateway             | String | ❌        |"internet_gateway"           | Enabling routing through Internet Gateway                                                                                                             |
| nat_gateway_name        | String | ❌        | all - false             | Enabling routing through NatGateway                                                                                                                   |
| rt_tags                 | String | ❌        |               | Routing tables tags                                                                                                                                   |
| subnets                 | String | ❌        |              | List of Subnets                                                                                                                                       |
| type_subnet             | String | ❌        |              | Type of subnets (Public or Private)                                                                                                                   |
| cidr_block              | String | ❌        |              | CIDR Block for the subnet                                                                                                                             |
| availability_zone       | String | ❌        |              | Availability zone for the subnet                                                                                                                      |
| map_public_ip_on_launch | String | ❌        |              | (Optional) Specify true to indicate that instances  launched into the subnet should be assigned a public IP address                                   |
| route_table_association | String | ❌        |              | Provides a resource to create an association between a  route table and a subnet or a route table and an internet  gateway or virtual private gateway.|
| rt_name                 | String | ❌        |              | (Required) The ID of the routing table to associate with.                                                                                             |
| tags                    | String | ❌        |              | Tags for the subnets                                                                                                                                  |
| internet_gateway        | String | ❌        | True         | Enable Internet Gatewa                                                                                                                                |
| security_groups         | String | ❌        |              | Security Group                                                                                                                                        |
| name                    | String | ❌        |              | Name of the security Group                                                                                                                            |
| ingress                 | String | ❌        |              | Ingress rules                                                                                                                                         |
| from_port               | String | ❌        |              | from port                                                                                                                                             |
| to_port                 | String | ❌        |              | to port                                                                                                                                               |
| protocol                | String | ❌        |              | protocol                                                                                                                                              |
| cidr_blocks             | String | ❌        |              | CIDR Block for the Ingress                                                                                                                            |
| engress                 | String | ❌        |              | Engress Ruless                                                                                                                                        |
| from_port               | String | ❌        |              | from port                                                                                                                                             |
| to_port                 | String | ❌        |              | to port                                                                                                                                               |
| protocol                | String | ❌        |              | protocol                                                                                                                                              |
| cidr_blocks             | String | ❌        |              | CIDR Block for the Engress                                                                                                                            
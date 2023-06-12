resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_cidr_block
}


### Internet Gateway ###

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
}


### NATGateway ###  
resource "aws_eip" "eip" {
  for_each = var.subnet_public
  depends_on = [
    aws_internet_gateway.internet_gateway
  ]
}

resource "aws_nat_gateway" "ngw" {
  for_each = var.subnet_public
  allocation_id = aws_eip.eip[each.key].id
  subnet_id     = aws_subnet.subnet_public[each.key].id
}

### Route Tables ###
resource "aws_route_table" "rt_public" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    
    gateway_id = aws_internet_gateway.internet_gateway.id
    
    
  }
  tags = {
        "Name" = "public-us-east-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/elb" = "1"
  }
}

resource "aws_route_table" "rt_rt" {
  for_each = var.subnet_private
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    
    
    nat_gateway_id = aws_nat_gateway.ngw[each.key].id
    
  }
  tags = {
        "Name" = "public-us-east-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/elb" = "1"
  }
}

### Subnets ###
resource "aws_subnet" "subnet_public" {
  for_each = var.subnet_public
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.availability_zone
  tags = {
        "Name" = "public-us-east-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/elb" = "1"
  }
}

### Route Table Association ###
resource "aws_route_table_association" "rta_public1" {
  for_each = var.subnet_public
  subnet_id      = aws_subnet.subnet_public[each.key].id
  route_table_id = aws_route_table.rt_public.id
}

resource "aws_subnet" "subnet_private" {
  for_each = var.subnet_private
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = each.value.cidr_block
  availability_zone = each.value.availability_zone
  tags = {
        "Name" = "public-us-east-1a"
        "kubernetes.io/cluster/eks" = "shared"
        "kubernetes.io/role/elb" = "1"
  }
}

### Route Table Association ###
resource "aws_route_table_association" "rta_private" {
  for_each = var.subnet_private
  subnet_id      = aws_subnet.subnet_private[each.key].id
  route_table_id = aws_route_table.rt_rt[each.key].id
}

resource "aws_security_group" "sg_in" {
  name = "sg_in"
  vpc_id = "${aws_vpc.vpc.id}"
  
  dynamic "ingress" {
    for_each = var.custom_ports
    
    content {
      from_port   = ingress.key
      to_port     = ingress.key
      protocol    = "tcp"
      cidr_blocks = ingress.value  
    }
      
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Environment = "test"
  }
}

output "public_id" {
  value = {for k,v in aws_subnet.subnet_public: k => v.id}
}
output "private_id" {
  value = {for k,v in aws_subnet.subnet_private: k => v.id}
}

output "security_group_id" {
  value = aws_security_group.sg_in.id
}

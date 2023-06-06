terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.0, < 5.0"
    }
  }
}

provider "aws" {
  region     = "us-east-1"
}


resource "aws_vpc" "vpc" {
  cidr_block = "{{ vpc_cidr_block }}"
}


### Internet Gateway ###
{% if internet_gateway %}
resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
}
{% endif %}

### NATGateway ###
{%- for ngw in nat_gateways %}
resource "aws_eip" "eip_{{loop.index}}" {
  depends_on = [
    aws_internet_gateway.internet_gateway
  ]
}

resource "aws_nat_gateway" "{{ ngw.nat_gateway_name }}" {
  allocation_id = aws_eip.eip_{{loop.index}}.id
  subnet_id     = aws_subnet.{{ ngw.for_subnet }}.id
}
{% endfor %}


### Route Tables ###
{%- for rt in route_tables %}
resource "aws_route_table" "rt_{{ rt.rt_name }}" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block     = "{{ rt.rt_cidr_block }}"
    {% if rt.int_gateway %}
    gateway_id = aws_internet_gateway.internet_gateway.id
    {% endif %}
    {% if rt.nat_gateway_name %}
    nat_gateway_id = aws_nat_gateway.{{ rt.nat_gateway_name }}.id
    {% endif %}
  }
  tags = {
    {%- for t,k in rt.rt_tags.items() %}
        "{{t}}" = "{{k}}"
    {%- endfor %}
  }
}
{% endfor %}


### Subnets ###
{%- for subnet in subnets %}
resource "aws_subnet" "{{ subnet.type_subnet }}" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "{{ subnet.cidr_block }}"
  availability_zone = "{{ subnet.availability_zone }}"
  tags = {
    {%- for t,k in subnet.tags.items() %}
        "{{t}}" = "{{k}}"
    {%- endfor %}
  }
}

### Route Table Association ###
{%- if subnet.route_table_association %}
resource "aws_route_table_association" "rta_{{ subnet.type_subnet }}" {
  subnet_id      = aws_subnet.{{ subnet.type_subnet }}.id
  route_table_id = aws_route_table.rt_{{ subnet.rt_name }}.id
}
{% endif %}
{% endfor %}


{%- for security in security_groups %}
resource "aws_security_group" "{{ security.name }}" {
  name = "{{ security.name }}"
  vpc_id = "${aws_vpc.vpc.id}"
  {% for ing in security.ingress %}
  ingress {
      from_port   = {{ ing.from_port }}
      to_port     = {{ ing.to_port}}
      protocol    = "{{ ing.protocol }}"
      cidr_blocks = {{ ing.cidr_blocks | safe }}
  }
  {% endfor %}
  {% for eng in security.engress %}
  egress {
    from_port   = {{ eng.from_port}}
    to_port     = {{ eng.to_port }}
    protocol    = "{{ eng.protocol }}"
    cidr_blocks = {{ eng.cidr_blocks | safe }}
  }
  {% endfor %}
  tags = {
    Environment = "test"
  }
}
{% endfor %}

{% for out_subnet_id in subnets %}
output "id_{{ out_subnet_id.type_subnet }}" {
  value = aws_subnet.{{ out_subnet_id.type_subnet }}.id
}
{% endfor %}

{%- for security in security_groups %}
output "id_{{ security.name }}" {
  value = aws_security_group.{{ security.name }}.id
}
{% endfor %}
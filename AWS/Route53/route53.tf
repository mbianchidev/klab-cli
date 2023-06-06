terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.0, < 5.0"
    }
  }
}

provider "aws" {
  region     = "eu-west-1"
}

resource "aws_route53_zone" "zone-{{ zone_domain_suffix }}" {
  name = "{{ zone_domain_name }}"
}

{% if private_zone == true -%}
resource "aws_route53_vpc_association_authorization" "{{ vpc_authorization_name }}" {
  vpc_id  = "{{ vpc_id }}"
  zone_id = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  vpc_region = "{{ vpc_region }}"
}

resource "aws_route53_zone_association" "{{ vpc_association }}" {
  vpc_id  = aws_route53_vpc_association_authorization.{{ vpc_authorization_name }}.vpc_id
  zone_id = aws_route53_vpc_association_authorization.{{ vpc_authorization_name }}.zone_id
  vpc_region = aws_route53_vpc_association_authorization.{{ vpc_authorization_name }}.vpc_region
}
{%- endif %}

resource "aws_route53_record" "record-{{ zone_domain_suffix }}" {
  zone_id = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  name    = "{{ zone_domain_name }}"
  type    = "A"
  ttl     = "{{ zone_domain_ttl }}"
  records = ["{{ zone_domain_ip }}"]
}

{% if with_elb == true -%}
{%- for elb in elbs %}
resource "aws_elb" "{{ elb.elb_name }}" {
  name               = "{{ elb.elb_name }}"
  instances          = [
    {%- for instance in elb.elb_instances -%}
    "{{ instance.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
  availability_zones = [
    {%- for availability_zone in elb.elb_availability_zones -%}
    "{{ availability_zone.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  {%- for listener in elb.elb_listeners %}
  listener {
    instance_port     = {{ listener.port }}
    instance_protocol = "{{ listener.protocol }}"
    lb_port           = {{ listener.lb_port }}
    lb_protocol       = "{{ listener.lb_protocol }}"
    {%- if listener.ssl_certificate_id is defined and listener.ssl_certificate_id != "" %}
    ssl_certificate_id = "{{ listener.ssl_certificate_id }}"
    {%- endif %}
  }
  {%- endfor %}

  health_check {
    healthy_threshold   = {{ elb.elb_healthy_threshold }}
    unhealthy_threshold = {{ elb.elb_unhealthy_threshold }}
    timeout             = {{ elb.elb_timeout }}
    target              = "{{ elb.elb_target }}"
    interval            = {{ elb.elb_interval }}
  }

  {%- if elb.elb_s3_bucket_name is defined and elb.elb_bucket_prefix is defined %}
  access_logs {
    bucket        = "{{ elb.elb_s3_bucket_name }}"
    bucket_prefix = "{{ elb.elb_bucket_prefix }}"
    interval      = 60
  }
  {%- endif %}
}
{% endfor %}
{%- endif %}

{% for record in records -%}
resource "aws_route53_record" "{{ record.label }}" {
  zone_id = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  name    = "{{ record.name }}"
{%- if record.protocol is defined %}
  {%- if record.protocol == "ipv6" %}
  type = "AAAA"
  {%- elif record.protocol == "ipv4" %}
  type = "A"
  {%- endif %}
{%- else %}
  type = "{{ record.type }}"
{%- endif %}
  {%- if record.aliases is not defined %}
  records = [
    {%- for target in record.targets %}
    "{{ target.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
  ttl             = "{{ record.ttl | default(600) }}"
  {%- endif %}
  allow_overwrite = {{ record.allow_overwrite|string|lower | default("false", true) }}

  {%- if record.weight is defined %}
  weighted_routing_policy {
    weight = {{ record.weight }}
  }
  set_identifier = "{% if record.identifier is defined %}{{ record.identifier }}{% else %}{{ record.name }}{% endif %}"
  {%- endif %}
  {%- if record.aliases is defined and record.aliases|length > 0 %}
  {%- for alias in record.aliases %}
  alias {
    name                   = "{{ alias.target_dns_name }}"
    zone_id                = "{{ alias.target_zone_id }}"
    evaluate_target_health = {{ alias.target_health|string|lower | default("true") }}
  }
  {%- endfor %}
  {%- endif %}

  {%- if tags is defined -%}
  tags = {
    {%- for tag in tags -%}
    {{ tag | safe -}}
    {%- endfor -%}
  }
  {%- endif %}
}

{% endfor %}

{%- if with_subdomains == true %}
variable "subdomains" {
  type    = list(string)
  default = [
    {%- for subdomain in subdomains -%}
    "{{ subdomain.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
}
{% for subdomain in subdomains %}
resource "aws_route53_record" "{{ subdomain.label }}" {
  zone_id = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  name    = "{{ subdomain.name }}.{{ zone_domain_name }}"
  type    = "A"
  ttl     = "{{ subdomain.ttl }}"
  records = ["{{ subdomain.ip }}"]
}

{% endfor %}
{%- endif %}

{%- if with_TXT_management == true %}
resource "aws_route53_record" "txt-record-{{ zone_domain_suffix }}" {
  name    = "{{ zone_domain_name }}"
  ttl     = 3600
  type    = "TXT"
  zone_id = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id

  records = [
    {%- for txt in TXT_values %}
    "{{ txt.value }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
}
{%- endif %}

{%- if with_NS_management == true %}
resource "aws_route53_record" "ns-record-{{ zone_domain_suffix }}" {
  name            = "{{ zone_domain_name }}"
  ttl             = 172800
  type            = "NS"
  zone_id         = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  allow_overwrite = true

  records = [
    {%- for name_server in NS_name_servers %}
    "{{ name_server.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
}
{%- endif %}

{%- if with_SOA_management == true %}
resource "aws_route53_record" "soa-record-{{ zone_domain_suffix }}" {
  name            = "{{ zone_domain_name }}"
  ttl             = 900
  type            = "SOA"
  zone_id         = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  allow_overwrite = true

  records = [
    {%- for name_server in SOA_name_servers %}
    "{{ name_server.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
}
{%- endif %}

{%- if with_MX_management == true %}
resource "aws_route53_record" "mx-record-{{ zone_domain_suffix }}" {
  name            = "{{ zone_domain_name }}"
  ttl             = 3600
  type            = "MX"
  zone_id         = aws_route53_zone.zone-{{ zone_domain_suffix }}.zone_id
  allow_overwrite = true

  records = [
    {%- for mail_server in MX_mail_servers %}
    "{{ mail_server.priority }} {{ mail_server.name }}"{% if not loop.last %},
    {%- endif -%}
    {%- endfor -%}
  ]
}
{%- endif %}

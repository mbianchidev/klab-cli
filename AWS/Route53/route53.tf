terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.0, < 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_route53_zone" "hosting_zone" {
  name = var.zone_domain_name
}

resource "aws_route53_vpc_association_authorization" "vpc_auth" {
  count      = var.enable_private_zone ? 1 : 0
  vpc_id     = var.vpc_id
  zone_id    = aws_route53_zone.hosting_zone.zone_id
  vpc_region = var.vpc_region
}

resource "aws_route53_zone_association" "vpc_association" {
  count      = var.enable_private_zone ? 1 : 0
  vpc_id     = aws_route53_vpc_association_authorization.vpc_auth[0].vpc_id
  zone_id    = aws_route53_vpc_association_authorization.vpc_auth[0].zone_id
  vpc_region = aws_route53_vpc_association_authorization.vpc_auth[0].vpc_region
}

resource "aws_route53_record" "zone_domain_record" {
  zone_id = aws_route53_zone.hosting_zone.zone_id
  name    = var.zone_domain_name
  type    = "A"
  ttl     = var.zone_domain_ttl
  records = [var.zone_domain_ip]
}


resource "aws_route53_record" "subdomain" {
  for_each = var.subdomain
  zone_id  = aws_route53_zone.hosting_zone.zone_id
  name     = each.value.subdomain_name
  type     = "A"
  ttl      = each.value.subdomain_ttl
  records  = [each.value.subdomain_ip]
}

resource "aws_route53_record" "ns-record" {
  count           = var.with_ns_record ? 1 : 0
  name            = var.zone_domain_name
  ttl             = var.ns_record_ttl
  type            = "NS"
  zone_id         = aws_route53_zone.hosting_zone.zone_id
  allow_overwrite = var.ns_record_allow_overwrite
  records         = var.nameservers
}


resource "aws_route53_record" "txt-record" {
  count   = var.with_txt_record ? 1 : 0
  name    = var.zone_domain_name
  ttl     = var.txt_record_ttl
  type    = "TXT"
  zone_id = aws_route53_zone.hosting_zone.zone_id
  records = var.txt_record_values
}

resource "aws_route53_record" "soa-record" {
  count           = var.with_soa_record ? 1 : 0
  name            = var.zone_domain_name
  ttl             = var.soa_record_ttl
  type            = "SOA"
  zone_id         = aws_route53_zone.hosting_zone.zone_id
  allow_overwrite = var.soa_record_allow_overwrite
  records         = var.soa_record_values
}


resource "aws_route53_record" "mx-record" {
  count           = var.with_mx_record ? 1 : 0
  name            = var.zone_domain_name
  ttl             = var.mx_record_ttl
  type            = "MX"
  zone_id         = aws_route53_zone.hosting_zone.zone_id
  allow_overwrite = var.mx_record_allow_overwrite
  records         = var.mx_record_values
}

resource "aws_route53_record" "weighted-record" {
  for_each        = var.weighted_record
  zone_id         = aws_route53_zone.hosting_zone.zone_id
  name            = each.value.record_name
  type            = each.value.record_type
  ttl             = each.value.record_ttl
  allow_overwrite = each.value.record_allow_overwrite
  records         = each.value.record_values
  set_identifier  = each.value.set_identifier
  weighted_routing_policy {
    weight = each.value.weight
  }
}

resource "aws_elb" "load_balancer" {
  count                       = var.with_elb ? 1 : 0
  name                        = var.elb_name
  availability_zones          = var.elb_availability_zones
  cross_zone_load_balancing   = var.elb_cross_zone_load_balancing
  idle_timeout                = var.elb_idle_timeout
  connection_draining         = var.elb_connection_draining
  connection_draining_timeout = var.elb_connection_draining_timeout

  dynamic "listener" {
    for_each = var.elb_listeners
    content {
      instance_port     = listener.key
      instance_protocol = listener.value
      lb_port           = listener.key
      lb_protocol       = listener.value
    }
  }

  health_check {
    healthy_threshold   = var.elb_healthy_threshold
    unhealthy_threshold = var.elb_unhealthy_threshold
    timeout             = var.elb_timeout
    target              = var.elb_target
    interval            = var.elb_interval
  }
}

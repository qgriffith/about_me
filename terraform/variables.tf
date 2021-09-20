variable "route53zone" {
  description = "Route53 Zone to use"
  default     = "qgriffith.me."
}

variable "subdomain" {
  description = "Subdomain to use as the CNAME"
  default     = "about"
}
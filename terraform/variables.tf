variable "bucket" {
  description = "Name of the s3 bucket to create"
  default     = "qgriffith-about-me-site"
}

variable "route53zone" {
  description = "Route53 Zone to use"
  default     = "qgriffith.me."
}

variable "subdomain" {
  description = "Subdomain to use as the CNAME"
  default     = "about"
}

variable "domain" {
  description = "Domain to use as the CNAME"
  default     = "qgriffith.me"
}
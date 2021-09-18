data "aws_route53_zone" "hostedzone" {
  name         = var.route53zone
  private_zone = false
}

resource "aws_s3_bucket" "qgriffith-about-me" {
  bucket = "qgriffith-about-me-site"
  acl    = "public-read"
  policy = file("policy.json")
versioning {
    enabled = true
  }
  website {
    index_document = "index.html"
    error_document = "error.html"
   
  }
}

resource "aws_route53_record" "about" {
  zone_id = data.aws_route53_zone.hostedzone.zone_id
  name    = var.subdomain
  type    = "CNAME"
  ttl     = "300"
  records = [aws_s3_bucket.qgriffith-about-me.website_endpoint]
}
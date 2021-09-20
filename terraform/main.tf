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

resource "aws_acm_certificate" "cert" {
  domain_name = format("%s.%s", var.subdomain, data.aws_route53_zone.hostedzone.name )
  validation_method = "DNS"
  provider = aws.use1
}

resource "aws_route53_record" "cert_validation" {
  allow_overwrite = true
  name            = tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_name
  records         = [ tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_value ]
  type            = tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_type
  zone_id  = data.aws_route53_zone.hostedzone.id
  ttl      = 60
}

resource "aws_acm_certificate_validation" "validate" {
  certificate_arn = "${aws_acm_certificate.cert.arn}"
  validation_record_fqdns = [aws_route53_record.cert_validation.fqdn,]
  provider = aws.use1
}

resource "aws_cloudfront_distribution" "s3frontend" {
  origin {
    custom_origin_config {
      http_port              = "80"
      https_port             = "443"
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.1", "TLSv1.2"]
    }

    domain_name = aws_s3_bucket.qgriffith-about-me.website_endpoint
    origin_id   = aws_s3_bucket.qgriffith-about-me.bucket
  }

  enabled             = true
  default_root_object = "index.html"


  default_cache_behavior {
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = aws_s3_bucket.qgriffith-about-me.bucket
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  price_class = "PriceClass_100"
  aliases = [format("%s.%s", var.subdomain, data.aws_route53_zone.hostedzone.name )]

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.cert.arn
    ssl_support_method  = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

resource "aws_route53_record" "subdomain" {
  zone_id = data.aws_route53_zone.hostedzone.zone_id
  name    = var.subdomain
  type    = "A"
  alias  {
    name                   = "${aws_cloudfront_distribution.s3frontend.domain_name}"
    zone_id                = "${aws_cloudfront_distribution.s3frontend.hosted_zone_id}"
    evaluate_target_health = false
  }
}
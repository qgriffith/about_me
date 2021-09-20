output "s3-website-endpoint" {
  description = "S3 URL"
  value       = aws_s3_bucket.content.website_endpoint
}

output "Cloudfront-ID" {
  description = "CloudFront ID"
  value       = aws_cloudfront_distribution.s3frontend.id
}
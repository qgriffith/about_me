output "s3-website-endpoint" {
  description = "S3 URL"
  value       = aws_s3_bucket.qgriffith-about-me.website_endpoint
}
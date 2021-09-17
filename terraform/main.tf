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
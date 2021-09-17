provider "aws" {
  region     = "us-east-2"
  profile    = "default"
}

terraform {
  backend "s3" {
    bucket = "qgriffith-terraform-state"
    key    = "about_me/terraform.tfstate"
    region = "us-east-2"
  }
}

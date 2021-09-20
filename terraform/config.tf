provider "aws" {
  region     = "us-east-2"
  profile    = "default"
}

provider "aws" {
  # us-east-1 instance
  region = "us-east-1"
  alias = "use1"
}

terraform {
  backend "s3" {
    bucket = "qgriffith-terraform-state"
    key    = "about_me/terraform.tfstate"
    region = "us-east-2"
  }
}

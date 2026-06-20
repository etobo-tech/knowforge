terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket  = "knowforge-tfstate-627407462314"
    key     = "terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
    profile = "knowforge"
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile != "" ? var.aws_profile : null
}

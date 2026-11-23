provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "Terraform"
      Environment = "sandbox"
      Purpose     = "platform-onboarding"
      Owner       = var.owner_tag
      Project     = var.project_tag
      Layer       = "customer-workload"
    }
  }
}

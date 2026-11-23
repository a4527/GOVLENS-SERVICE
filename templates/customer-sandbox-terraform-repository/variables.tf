variable "aws_region" {
  description = "Approved customer sandbox Region."
  type        = string
  default     = "us-east-1"
}

variable "sandbox_bucket_name" {
  description = "Globally unique, non-sensitive name for the first sandbox bucket."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.sandbox_bucket_name))
    error_message = "Use a 3-63 character lowercase S3-compatible bucket name."
  }
}

variable "owner_tag" {
  description = "Value of the common Owner tag (DEC-0030). Supplied by the GitHub Environment, not committed."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9._@+-]{1,128}$", var.owner_tag))
    error_message = "Provide a non-empty Owner tag value of up to 128 characters."
  }
}

variable "project_tag" {
  description = "Value of the common Project tag."
  type        = string
  default     = "govlens"
}

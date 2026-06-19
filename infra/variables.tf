variable "aws_region" {
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  default     = "knowforge"
  description = "AWS CLI profile for local runs. Leave empty in CI."
}

variable "project_name" {
  type        = string
  default     = "knowforge"
}

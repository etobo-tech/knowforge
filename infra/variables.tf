variable "aws_region" {
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  default     = "knowforge"
}

variable "project_name" {
  type        = string
  default     = "knowforge"
}

variable "lambda_runtime" {
  type        = string
  default     = "python3.13"
}

variable "lambda_architecture" {
  type        = string
  default     = "x86_64"
}

variable "database_url" {
  type        = string
  sensitive   = true
  description = "PostgreSQL connection string for the backend."
}

variable "openai_api_key" {
  type        = string
  sensitive   = true
  description = "OpenAI API key used by the RAG pipeline."
}

variable "cors_allowed_origins" {
  type        = list(string)
  default     = ["http://localhost:3000", "http://127.0.0.1:3000"]
  description = "Origins allowed to call the backend API."
}

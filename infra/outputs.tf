output "documents_bucket_name" {
  description = "Bucket for app uploads. Set S3_BUCKET in back/.env."
  value       = aws_s3_bucket.documents.id
}

output "terraform_state_bucket_name" {
  description = "Bucket for Terraform remote state (use in backend config)."
  value       = aws_s3_bucket.terraform_state.id
}

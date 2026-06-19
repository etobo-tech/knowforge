resource "aws_ecr_repository" "back" {
  name                 = "${var.project_name}-back"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "back" {
  repository = aws_ecr_repository.back.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 3 images"

      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 3
      }

      action = {
        type = "expire"
      }
    }]
  })
}

output "back_ecr_repository_url" {
  value = aws_ecr_repository.back.repository_url
}

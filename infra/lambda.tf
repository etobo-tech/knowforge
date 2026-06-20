# ================================
# KNOWFORGE BACK (Lambda container)
# Image is built and pushed to ECR manually from back/:
#   docker buildx build --platform linux/amd64 --provenance=false --load -t knowforge-back:latest .
# ================================

data "aws_ecr_image" "back" {
  repository_name = aws_ecr_repository.back.name
  image_tag       = "latest"
}

resource "aws_iam_role" "back_lambda" {
  name = "${var.project_name}-back-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "back_lambda_basic_execution" {
  role       = aws_iam_role.back_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "back_lambda_s3" {
  name = "${var.project_name}-back-lambda-s3"
  role = aws_iam_role.back_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
        ]
        Resource = "${aws_s3_bucket.documents.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
        ]
        Resource = aws_s3_bucket.documents.arn
      },
    ]
  })
}

resource "aws_cloudwatch_log_group" "back_lambda" {
  name              = "/aws/lambda/${var.project_name}-back"
  retention_in_days = 14
}

resource "aws_lambda_function" "back" {
  function_name = "${var.project_name}-back"
  role          = aws_iam_role.back_lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.back.repository_url}@${data.aws_ecr_image.back.image_digest}"
  architectures = [var.lambda_architecture]
  timeout       = 900
  memory_size     = 2048

  ephemeral_storage {
    size = 1024
  }

  environment {
    variables = {
      DATABASE_URL       = var.database_url
      OPENAI_API_KEY     = var.openai_api_key
      AWS_DEFAULT_REGION = var.aws_region
    }
  }

  depends_on = [
    data.aws_ecr_image.back,
    aws_cloudwatch_log_group.back_lambda,
    aws_iam_role_policy_attachment.back_lambda_basic_execution,
    aws_iam_role_policy.back_lambda_s3,
  ]
}

resource "aws_apigatewayv2_api" "back" {
  name          = "${var.project_name}-back"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.cors_allowed_origins
    allow_methods = ["*"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_integration" "back" {
  api_id                 = aws_apigatewayv2_api.back.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.back.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "back_default" {
  api_id    = aws_apigatewayv2_api.back.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.back.id}"
}

resource "aws_apigatewayv2_stage" "back" {
  api_id      = aws_apigatewayv2_api.back.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "back_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.back.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.back.execution_arn}/*/*"
}

output "back_lambda_function_name" {
  value = aws_lambda_function.back.function_name
}

output "back_api_endpoint" {
  value = aws_apigatewayv2_api.back.api_endpoint
}

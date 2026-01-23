data "archive_file" "zip_lambda_function" {
  type        = "zip"
  source_file = "${var.source_dir}/${var.function_name}.py"
  output_path = "${path.module}/${var.function_name}.zip"
}

resource "aws_lambda_function" "lambda" {
  filename      = data.archive_file.zip_lambda_function.output_path
  function_name = var.function_name
  role          = var.role_arn
  handler       = "${var.function_name}.handler"
  code_sha256   = data.archive_file.zip_lambda_function.output_base64sha256

  runtime     = var.config.runtime
  memory_size = var.config.memory_size
  timeout     = var.config.timeout

  environment {
    variables = var.env_variables
  }
} 
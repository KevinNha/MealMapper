data "archive_file" "zip_lambda_function" {
  type        = "zip"
  source_file = "${var.source_dir}/${var.function_name}.py"
  output_path = "${path.module}/${var.function_name}-${var.stage}.zip"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.function_name}-lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachments" {
  for_each   = toset(var.policy_arns)
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = each.value
}

resource "aws_lambda_function" "lambda" {
  filename      = data.archive_file.zip_lambda_function.output_path
  function_name = var.function_name
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "${var.function_name}.handler"
  code_sha256   = data.archive_file.zip_lambda_function.output_base64sha256

  runtime     = var.config.runtime
  memory_size = var.config.memory_size
  timeout     = var.config.timeout

  environment {
    variables = var.env_variables
  }
} 
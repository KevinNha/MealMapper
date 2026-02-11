module "lambda" {
  source        = "../modules/lambda"
  function_name = "extract-recipe"
  source_dir    = "../../src/extract-recipe"
  stage         = "dev"
  policy_arns   = { "extract_recipe" = aws_iam_policy.extract_recipe_policy.arn }
  env_variables = {
    LOG_LEVEL = "INFO"
  }
}
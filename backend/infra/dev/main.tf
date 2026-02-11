module "lambda" {
  source        = "../modules/lambda"
  function_name = "extract-recipe"
  source_dir    = "../../src"
  policy_arns   = []
  env_variables = {}
}
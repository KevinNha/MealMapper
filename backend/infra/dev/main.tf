# Build Lambda package: install deps (e.g. boto3) into build dir and copy function code.
# Terraform then zips this dir in the lambda module. Run from backend/infra/dev (path.module = .).
resource "null_resource" "build_extract_recipe" {
  triggers = {
    requirements = filemd5("${path.module}/../../src/extract-recipe/requirements.txt")
    source       = md5(join("", [for f in fileset("${path.module}/../../src/extract-recipe", "**") : filemd5("${path.module}/../../src/extract-recipe/${f}")]))
  }

  provisioner "local-exec" {
    command     = <<-EOT
      set -e
      BUILD_DIR="${path.module}/../../build/extract-recipe"
      SRC_DIR="${path.module}/../../src"
      REQ_FILE="${path.module}/../../src/extract-recipe/requirements.txt"
      mkdir -p "$BUILD_DIR"/shared
      pip install -r "$REQ_FILE" -t "$BUILD_DIR"
      cp "$SRC_DIR"/extract-recipe/*.py "$SRC_DIR"/extract-recipe/*.json "$BUILD_DIR/"
      cp "$SRC_DIR"/shared/*.py "$BUILD_DIR/"shared/
      [ -f "$SRC_DIR/mock_content.txt" ] && cp "$SRC_DIR/mock_content.txt" "$BUILD_DIR/" || true
    EOT
    working_dir = path.module
  }
}

module "lambda" {
  source        = "../modules/lambda"
  function_name = "extract-recipe"
  source_dir    = "${path.module}/../../build/extract-recipe"
  stage         = "dev"
  policy_arns   = { "extract_recipe" = aws_iam_policy.extract_recipe_policy.arn }
  env_variables = {
    LOG_LEVEL = "INFO"
  }

  depends_on = [null_resource.build_extract_recipe]
}
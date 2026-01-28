variable "stage" {
  description = "The stage of the Lambda function"
  type        = string
}

variable "source_dir" {
  description = "The directory containing the Lambda function code"
  type        = string
}

variable "function_name" {
  description = "The name of the Lambda function file"
  type        = string
}

variable "env_variables" {
  description = "The environment variables to pass to the Lambda function"
  type        = map(string)
  default     = {}
}

variable "policy_arns" {
  description = "The IAM policy ARNs to attach to the Lambda function"
  type        = list(string)
}

variable "config" {
  description = "The configuration for the Lambda function"
  type = object({
    memory_size = number
    timeout     = number
    runtime     = string
  })
  default = {
    memory_size = 512
    timeout     = 60
    runtime     = "python3.14"
  }
}
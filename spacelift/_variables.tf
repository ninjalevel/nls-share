variable "spacelift_aws_role_name" {
  description = "The name of the IAM role"
  type        = string
  default     = "my_role"
}

variable "spacelift_aws_stack_id" {
  description = "The ID of the stack"
  type        = string
  default     = "my-stack-id"
}

variable "spacelift_aws_module_id" {
  description = "The ID of the module"
  type        = string
  default     = "my-module-id"
}

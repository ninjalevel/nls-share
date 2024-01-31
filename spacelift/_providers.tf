terraform {
  required_version = ">= 1.6.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    spacelift = {
      source = "spacelift-io/spacelift"
      version = "1.8.0"
    }

  }

}

provider "aws" {
  # Configuration options:
  # 1. region: (Required) The region where AWS operations will be performed.
  # 2. profile: (Optional) This is the AWS credentials profile to use. If not set, the default profile from the AWS credentials file is used.
  region  = "ca-central-1"
  profile = "NLS-Not-Root"  # This is the default profile. It uses the [default] profile from the AWS credentials file.
}



provider "spacelift" {
  # Configuration options:
  # 1. alias: (Optional) Alias name to assign to the provider instance.
  # 2. api_endpoint: (Optional) The endpoint for the Spacelift API.
  # 3. api_token: (Optional) The token to authenticate with the Spacelift API.
  # 4. impersonate_account: (Optional) The ID of the account to impersonate.
}
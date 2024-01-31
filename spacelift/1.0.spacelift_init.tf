# winget install spacectl
# https://docs.spacelift.io/concepts/spacectl
# SET BROWSER
# spacectl profile login nls
# This is only for inteacting with spacectl, you need API keys to tf plan

# https://docs.spacelift.io/integrations/api
# choco install insomnia-rest-api-client
# create account
# Backup Key for Insomnia: bsalad
# Open Insomnia > New Graphql request
# spacectl profile export-token | clip


data "spacelift_account" "this" {}

output "spacelift_account_id" {
  value = data.spacelift_account.this
}


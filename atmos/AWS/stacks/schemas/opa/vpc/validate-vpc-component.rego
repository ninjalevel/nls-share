# ---- stacks/schemas/opa/vpc/validate-vpc-component.rego

# Atmos looks for the 'errors' (array of strings) output from all OPA policies
# If the 'errors' output contains one or more error messages, Atmos considers the policy failed

# 'package atmos' is required in all `atmos` OPA policies
package atmos

import future.keywords.in

# Import the constants from the file `stacks/schemas/opa/catalog/constants/constants.rego`
import data.atmos.constants.vpc_dev_max_availability_zones_error_message
import data.atmos.constants.vpc_prod_map_public_ip_on_launch_error_message
import data.atmos.constants.vpc_name_regex
import data.atmos.constants.vpc_name_regex_error_message

# In production, don't allow mapping public IPs on launch
errors[vpc_prod_map_public_ip_on_launch_error_message] {
    input.vars.stage == "prod"
    input.vars.map_public_ip_on_launch == true
}

# In 'dev', only 2 Availability Zones are allowed
errors[vpc_dev_max_availability_zones_error_message] {
    input.vars.stage == "dev"
    count(input.vars.availability_zones) != 2
}

# Check VPC name
errors[vpc_name_regex_error_message] {
    not re_match(vpc_name_regex, input.vars.name)
}
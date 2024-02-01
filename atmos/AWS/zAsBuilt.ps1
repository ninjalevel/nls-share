

$file = [pscustomobject]@{
    catalog = @{
        vpc_flow_logs_bucket = "stacks/catalog/vpc-flow-logs-bucket/defaults.yaml"
        vpc = "stacks/catalog/vpc/defaults.yaml"
    }
    mixins = @{
        tenant = @{
            core = "stacks/mixins/tenant/core.yaml"
            plat = "stacks/mixins/tenant/plat.yaml"
        }
        region = @{
            us_east_2 = "stacks/mixins/region/us-east-2.yaml"
            us_west_2 = "stacks/mixins/region/us-west-2.yaml"
        }
        stage = @{
            dev = "stacks/mixins/stage/dev.yaml"
            prod = "stacks/mixins/stage/prod.yaml"
            staging = "stacks/mixins/stage/staging.yaml"
        }
    }
    orgs = @{
        nls = @{
            core = @{
                _defaults = "stacks/orgs/nls/core/_defaults.yaml"
            }
            plat = @{
                _defaults = "stacks/orgs/nls/plat/_defaults.yaml"
                dev = @{
                    _defaults = "stacks/orgs/nls/plat/dev/_defaults.yaml"
                    # us_east_2 = "stacks/orgs/nls/plat/dev/us-east-2.yaml"
                    # us_west_2 = "stacks/orgs/nls/plat/dev/us-west-2.yaml"
                }
                prod = @{
                    _defaults = "stacks/orgs/nls/plat/prod/_defaults.yaml"
                    # us_east_2 = "stacks/orgs/nls/plat/prod/us-east-2.yaml"
                    # us_west_2 = "stacks/orgs/nls/plat/prod/us-west-2.yaml"
                }
                staging = @{
                    # us_east_2 = "stacks/orgs/nls/plat/staging/us-east-2.yaml"
                    # us_west_2 = "stacks/orgs/nls/plat/staging/us-west-2.yaml"
                }
            }
        }
    }
}

function Create-FileWithDirectories {
    param (
        [string]$filePath
    )
    $directoryPath = [System.IO.Path]::GetDirectoryName($filePath)
    if (-not (Test-Path -Path $directoryPath)) {
        New-Item -ItemType Directory -Path $directoryPath -Force
    }
    if (-not (Test-Path -Path $filePath)) {
        New-Item -ItemType File -Path $filePath
    }
}

# Create-FileWithDirectories -filePath $file

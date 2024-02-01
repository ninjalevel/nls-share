# Define the root directory
$rootDir = "C:\DHE\git\nls-infra\root_git\atmos\AWS\stacks" # Update this path as needed

function Create-DirectoryStructure {
    param (
        [string]$basePath,
        [string[]]$paths
    )

    foreach ($path in $paths) {
        $fullPath = Join-Path $basePath $path
        if (-not (Test-Path $fullPath)) {
            $type = if ($path -match "\.yaml$") { "file" } else { "directory" }
            New-Item -Path $fullPath -ItemType $type -Force | Out-Null
            Write-Host "Created $type at $fullPath"
        } else {
            Write-Host "$type at $fullPath already exists."
        }
    }
}


# Define the directory and file structure relative to $rootDir
$paths = @(
    "catalog",
    "catalog\vpc-flow-logs-bucket",
    "catalog\vpc-flow-logs-bucket\defaults.yaml",
    "catalog\vpc",
    "catalog\vpc\defaults.yaml",
    "catalog\account",
    "catalog\account\defaults.yaml",
    "mixins",
    "mixins\tenant",
    "mixins\tenant\core.yaml",
    "mixins\tenant\plat.yaml",
    "mixins\region",
    "mixins\region\global-region.yaml",
    "mixins\region\us-east-2.yaml",
    "mixins\stage",
    "mixins\stage\root.yaml",
    "mixins\stage\prod.yaml",
    "orgs",
    "orgs\org1",
    "orgs\org1\_defaults.yaml",
    "orgs\org1\core",
    "orgs\org1\core\_defaults.yaml",
    "orgs\org1\core\root",
    "orgs\org1\core\root\_defaults.yaml",
    "orgs\org1\core\root\global-region.yaml",
    "orgs\org1\core\root\us-east-2.yaml",
    "orgs\org1\plat",
    "orgs\org1\plat\_defaults.yaml",
    "orgs\org1\plat\prod",
    "orgs\org1\plat\prod\_defaults.yaml",
    "orgs\org1\plat\prod\global-region.yaml",
    "orgs\org1\plat\prod\us-east-2.yaml"
)

# Create the directory structure
# Create-DirectoryStructure -basePath $rootDir -paths $paths

Write-Host "Directory structure created successfully."

function Find-EmptyYamlFiles {
    param (
        [string]$basePath
    )

    # Get all .yaml files in the directory and its subdirectories
    $yamlFiles = Get-ChildItem -Path $basePath -Recurse -Filter "*.yaml"

    # Filter for empty files
    $emptyYamlFiles = $yamlFiles | Where-Object { $_.Length -eq 0 }

    if ($emptyYamlFiles.Count -eq 0) {
        Write-Host "No empty YAML files found."
    } else {
        Write-Host "Empty YAML files found:"
        foreach ($file in $emptyYamlFiles) {
            Write-Host ($file.FullName -replace '\\', '/')
        }
    }
}
Find-EmptyYamlFiles -basePath $rootDir 

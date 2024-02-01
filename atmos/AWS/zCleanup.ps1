$Paths = [pscustomobject]@{
    TerraformDir = "C:\DHE\git\nls-infra\root_git\atmos\AWS\components\terraform"
    LogsDir      = "C:\DHE\git\nls-infra\root_git\atmos\AWS\logs"
}
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne 'main') {
    Remove-Item -Path $Paths.TerraformDir, $Paths.LogsDir -Recurse -Force
}


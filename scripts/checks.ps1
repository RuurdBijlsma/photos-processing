function Run-Checks
{
    param ([string]$dir)
    Write-Host "================================  $dir  ================================"
    Push-Location $dir
    poetry run pre-commit run --all-files
    poetry run mypy . --strict --ignore-missing-imports
    Pop-Location
}

Push-Location $PSScriptRoot/..
Run-Checks -dir photos-server
Pop-Location

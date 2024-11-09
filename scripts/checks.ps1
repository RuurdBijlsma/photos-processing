function Run-Checks
{
    param ([string]$dir)
    Write-Host "================================  $dir  ================================"
    Push-Location $dir
    poetry run pre-commit run --all-files
    poetry run mypy -p photos --strict --ignore-missing-imports
    poetry run mypy -p tests --strict --ignore-missing-imports
    Pop-Location
}

Push-Location $PSScriptRoot/..
Run-Checks -dir ./
Pop-Location

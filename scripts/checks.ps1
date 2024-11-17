function Run-Checks
{
    param ([string]$dir)
    Write-Host "================================  $dir  ================================"
    Push-Location $dir
    uv run ruff check . --fix
    uv run mypy -p app --strict --ignore-missing-imports
    uv run mypy -p tests --strict --ignore-missing-imports
    Pop-Location
}

Push-Location $PSScriptRoot/..
Run-Checks -dir ./
Pop-Location

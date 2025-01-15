Push-Location $PSScriptRoot/..

uv run ruff check . --fix
uv run pyscan
uv run mypy -p app --strict --ignore-missing-imports
uv run mypy -p tests --strict --ignore-missing-imports
uv run pylint `
    --output-format=colorized `
    --fail-under 9 `
    app/**/*.py tests/**/*.py

Pop-Location



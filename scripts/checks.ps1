Push-Location $PSScriptRoot/..

uv run ruff check . --fix
#uv run mypy -p app --strict --ignore-missing-imports
#uv run mypy -p tests --strict --ignore-missing-imports
uv run pylint --disable=C0114,C0115,C0116,R0903,C0415,E1101,E1102,R0917,R0913,C0103,R0901,C0411 app/**/*.py tests/**/*.py

Pop-Location



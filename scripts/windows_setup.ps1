$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playwright install chromium
python -m avito_clicker doctor

[CmdletBinding()]
param(
    [switch]$Fix
)

$ErrorActionPreference = "Stop"

$python = Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        throw "Python nao encontrado. Crie a virtualenv (.venv) conforme o README.md."
    }
    $python = $pythonCmd.Source
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if ($Fix) {
        & $python -m ruff format .
        & $python -m ruff check --fix .
    } else {
        Write-Host "==> 1. Verificando formatacao (ruff format --check)..."
        & $python -m ruff format --check --diff .
        if ($LASTEXITCODE -ne 0) { throw "Falha na verificacao de formatacao." }

        Write-Host "==> 2. Executando linter (ruff check)..."
        & $python -m ruff check .
        if ($LASTEXITCODE -ne 0) { throw "Falha no linter." }
    }

    Write-Host "==> 3. Verificando build reproduzivel (compileall)..."
    $targets = @("tests")
    if (Test-Path "dev") { $targets += "dev" }
    if (Test-Path "scripts") { $targets += "scripts" }
    if (Test-Path "api") { $targets += "api" }
    & $python -m compileall -q @targets
    if ($LASTEXITCODE -ne 0) { throw "Falha na compilacao Python." }

    Write-Host "==> 4. Executando testes e cobertura..."
    if ((Test-Path "api\eventfy_api\main.py") -and (Test-Path "tests\test_api.py")) {
        $env:PYTHONPATH = "api"
        & $python -m pytest --cov=api/eventfy_api --cov-report=term-missing --cov-report=xml:coverage.xml
    } else {
        $env:PYTHONPATH = "dev"
        & $python -m pytest --cov=dev --cov-report=term-missing --cov-report=xml:coverage.xml
    }
    if ($LASTEXITCODE -ne 0) { throw "Falha na execucao dos testes." }

    Write-Host "Todas as verificacoes de qualidade passaram."
} finally {
    Pop-Location
}

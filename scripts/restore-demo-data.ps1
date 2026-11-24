[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$Server = $(if ($env:PGHOST) { $env:PGHOST } else { "localhost" }),
    [ValidateRange(1, 65535)]
    [int]$Port = $(if ($env:PGPORT) { [int]$env:PGPORT } else { 5432 }),
    [ValidatePattern('^eventfy_demo(?:_[A-Za-z0-9_]+)?$')]
    [string]$Database = "eventfy_demo",
    [string]$Username = $(if ($env:PGUSER) { $env:PGUSER } else { "postgres" })
)

$ErrorActionPreference = "Stop"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$databaseSetup = Join-Path $PSScriptRoot "db-setup.ps1"
$seedFile = Join-Path $repositoryRoot "db\migrations\V2__seed_demo_data.sql"
if (-not (Test-Path -LiteralPath $databaseSetup -PathType Leaf)) {
    throw "Script de preparacao do banco nao encontrado: $databaseSetup"
}
if (-not (Test-Path -LiteralPath $seedFile -PathType Leaf)) {
    throw "Migracao de dados de demonstracao nao encontrada: $seedFile"
}

if (-not $PSCmdlet.ShouldProcess(
    "banco '$Database' em $Server`:$Port",
    "substituir os dados pelas fixtures de demonstracao"
)) {
    return
}

& $databaseSetup -Server $Server -Port $Port -Database $Database -Username $Username

$psql = Get-Command psql -ErrorAction Stop
$seedSql = Get-Content -LiteralPath $seedFile -Raw
$restoreSql = @"
BEGIN;
TRUNCATE TABLE
    public.avaliacao,
    public.historico_reserva,
    public.reserva,
    public.arquivo,
    public.disponibilidade_servico,
    public.servico,
    public.evento,
    public.usuario
RESTART IDENTITY;
$seedSql
COMMIT;
"@

$temporaryFile = [System.IO.Path]::GetTempFileName()
try {
    [System.IO.File]::WriteAllText(
        $temporaryFile,
        $restoreSql,
        [System.Text.UTF8Encoding]::new($false)
    )

    $arguments = @(
        "--no-psqlrc",
        "--set=ON_ERROR_STOP=1",
        "--host", $Server,
        "--port", "$Port",
        "--username", $Username,
        "--dbname", $Database,
        "--file", $temporaryFile
    )
    & $psql.Source @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao restaurar os dados de demonstracao no banco '$Database'."
    }

    Write-Host "Dados de demonstracao restaurados em '$Database'."
} finally {
    Remove-Item -LiteralPath $temporaryFile -Force -ErrorAction SilentlyContinue
}

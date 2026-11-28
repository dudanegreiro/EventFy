[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z_][A-Za-z0-9_]*$')]
    [string]$Database = 'eventfy',
    [Parameter(Mandatory)]
    [string]$OutputFile,
    [string]$Server = $(if ($env:PGHOST) { $env:PGHOST } else { 'localhost' }),
    [ValidateRange(1, 65535)]
    [int]$Port = $(if ($env:PGPORT) { [int]$env:PGPORT } else { 5432 }),
    [string]$Username = $(if ($env:PGUSER) { $env:PGUSER } else { 'postgres' })
)

$ErrorActionPreference = 'Stop'
$pgDump = Get-Command pg_dump -ErrorAction Stop
$destination = [System.IO.Path]::GetFullPath($OutputFile)
$parent = Split-Path -Parent $destination
if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
    throw "Diretorio de backup inexistente: $parent"
}
if (Test-Path -LiteralPath $destination) {
    throw "O arquivo de backup ja existe: $destination"
}

& $pgDump.Source --format=custom --no-owner --no-privileges --host $Server --port $Port --username $Username --dbname $Database --file $destination
if ($LASTEXITCODE -ne 0) {
    Remove-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
    throw "pg_dump falhou para o banco '$Database'."
}
Write-Host "Backup criado: $destination"

[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidatePattern('^[A-Za-z_][A-Za-z0-9_]*$')]
    [string]$Database = 'eventfy',
    [Parameter(Mandatory)]
    [string]$BackupFile,
    [string]$Server = $(if ($env:PGHOST) { $env:PGHOST } else { 'localhost' }),
    [ValidateRange(1, 65535)]
    [int]$Port = $(if ($env:PGPORT) { [int]$env:PGPORT } else { 5432 }),
    [string]$Username = $(if ($env:PGUSER) { $env:PGUSER } else { 'postgres' })
)

$ErrorActionPreference = 'Stop'
$pgRestore = Get-Command pg_restore -ErrorAction Stop
$backup = (Resolve-Path -LiteralPath $BackupFile -ErrorAction Stop).Path
if ($Database -in @('postgres', 'template0', 'template1')) {
    throw "Recusa restaurar sobre banco de sistema: $Database"
}
if (-not $PSCmdlet.ShouldProcess($Database, "Substituir todos os objetos pelo backup '$backup'")) {
    return
}

& $pgRestore.Source --clean --if-exists --no-owner --no-privileges --exit-on-error --host $Server --port $Port --username $Username --dbname $Database $backup
if ($LASTEXITCODE -ne 0) {
    throw "pg_restore falhou para o banco '$Database'."
}
Write-Host "Restauracao concluida: $Database"

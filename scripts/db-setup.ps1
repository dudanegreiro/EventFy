[CmdletBinding()]
param(
    [string]$Server = $(if ($env:PGHOST) { $env:PGHOST } else { "localhost" }),
    [ValidateRange(1, 65535)]
    [int]$Port = $(if ($env:PGPORT) { [int]$env:PGPORT } else { 5432 }),
    [ValidatePattern('^[A-Za-z_][A-Za-z0-9_]*$')]
    [string]$Database = "eventfy",
    [string]$Username = $(if ($env:PGUSER) { $env:PGUSER } else { "postgres" })
)

$ErrorActionPreference = "Stop"

$psql = Get-Command psql -ErrorAction SilentlyContinue
$createdb = Get-Command createdb -ErrorAction SilentlyContinue
if (-not $psql -or -not $createdb) {
    throw "PostgreSQL client tools psql e createdb devem estar no PATH."
}

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$migrationDirectory = Join-Path $repositoryRoot "db\migrations"
$migrationFiles = @(Get-ChildItem -LiteralPath $migrationDirectory -Filter "V*__*.sql" -File)
if ($migrationFiles.Count -eq 0) {
    throw "Nenhuma migracao encontrada em $migrationDirectory."
}

$migrations = foreach ($file in $migrationFiles) {
    if ($file.Name -notmatch '^V(?<version>[0-9]+)__(?<description>[A-Za-z0-9_-]+)\.sql$') {
        throw "Nome de migracao invalido: $($file.Name). Use V<numero>__<descricao>.sql."
    }

    [pscustomobject]@{
        Version = [int]$Matches.version
        File = $file
    }
}
$migrations = @($migrations | Sort-Object Version)
if (($migrations.Version | Select-Object -Unique).Count -ne $migrations.Count) {
    throw "Ha versoes de migracao duplicadas."
}

function Invoke-Psql {
    param(
        [string]$TargetDatabase,
        [string[]]$ExtraArguments
    )

    $arguments = @(
        "--no-psqlrc",
        "--set=ON_ERROR_STOP=1",
        "--host", $Server,
        "--port", "$Port",
        "--username", $Username,
        "--dbname", $TargetDatabase
    ) + $ExtraArguments

    & $psql.Source @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "psql falhou ao conectar ao banco '$TargetDatabase'."
    }
}

$databaseExists = Invoke-Psql -TargetDatabase "postgres" -ExtraArguments @(
    "--tuples-only",
    "--no-align",
    "--command", "SELECT 1 FROM pg_database WHERE datname = '$Database';"
)

if (($databaseExists | Out-String).Trim() -ne "1") {
    & $createdb.Source "--host" $Server "--port" "$Port" "--username" $Username "--owner" $Username $Database
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel criar o banco '$Database'. Verifique as permissoes do usuario '$Username'."
    }
    Write-Host "Banco '$Database' criado."
} else {
    Write-Host "Banco '$Database' ja existe."
}

Invoke-Psql -TargetDatabase $Database -ExtraArguments @(
    "--command",
    "CREATE TABLE IF NOT EXISTS public.schema_migrations (version integer PRIMARY KEY, checksum char(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT now());"
) | Out-Null

$appliedOutput = Invoke-Psql -TargetDatabase $Database -ExtraArguments @(
    "--tuples-only",
    "--no-align",
    "--command", "SELECT version || '|' || checksum FROM public.schema_migrations ORDER BY version;"
)
$applied = @{}
foreach ($line in ($appliedOutput | ForEach-Object { "$_".Trim() })) {
    if ($line) {
        $parts = $line -split '\|', 2
        $applied[[int]$parts[0]] = $parts[1].Trim()
    }
}

foreach ($migration in $migrations) {
    $version = $migration.Version
    $checksum = (Get-FileHash -LiteralPath $migration.File.FullName -Algorithm SHA256).Hash.ToLowerInvariant()

    if ($applied.ContainsKey($version)) {
        if ($applied[$version] -ne $checksum) {
            throw "A migracao $($migration.File.Name) foi alterada depois de aplicada. Crie uma nova migracao."
        }
        Write-Host "Migracao V$version ja aplicada."
        continue
    }

    $sql = @"
BEGIN;
$(Get-Content -LiteralPath $migration.File.FullName -Raw)
INSERT INTO public.schema_migrations (version, checksum) VALUES ($version, '$checksum');
COMMIT;
"@
    $temporaryFile = [System.IO.Path]::GetTempFileName()
    try {
        [System.IO.File]::WriteAllText(
            $temporaryFile,
            $sql,
            [System.Text.UTF8Encoding]::new($false)
        )
        Invoke-Psql -TargetDatabase $Database -ExtraArguments @("--file", $temporaryFile) | Out-Null
        Write-Host "Migracao V$version aplicada: $($migration.File.Name)"
    } finally {
        Remove-Item -LiteralPath $temporaryFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Banco '$Database' pronto."

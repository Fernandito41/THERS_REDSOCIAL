<#
.SYNOPSIS
    Corre las verificaciones del proyecto: pytest del backend y, opcionalmente,
    lint y build del frontend.

.DESCRIPTION
    Automatiza docs/LOCAL_DEV_SETUP.md seccion 5. Resuelve por su cuenta las dos
    cosas que hacen fallar a pytest en local:

      - deriva TEST_DATABASE_URL de DATABASE_URL (backend/.env), en vez de
        confiar en el puerto 5432 que asume backend/tests/conftest.py;
      - aplica las migraciones pendientes a thers_test antes de correr.

    Los tests corren contra PostgreSQL real y truncan las tablas de thers_test
    entre casos. Nunca tocan thers_dev.

.PARAMETER Frontend
    Corre tambien lint y build del frontend.

.PARAMETER FrontendOnly
    Corre solo lint y build del frontend, sin pytest.

.PARAMETER SkipMigrations
    No aplica migraciones a thers_test antes de correr los tests.

.PARAMETER PytestArgs
    Argumentos extra que se pasan tal cual a pytest.

.EXAMPLE
    .\scripts\dev-test.ps1

.EXAMPLE
    .\scripts\dev-test.ps1 -Frontend

.EXAMPLE
    .\scripts\dev-test.ps1 -PytestArgs "-k","posts","-v"
#>
[CmdletBinding()]
param(
    [switch]$Frontend,
    [switch]$FrontendOnly,
    [switch]$SkipMigrations,
    [string[]]$PytestArgs = @()
)

. (Join-Path $PSScriptRoot "_lib.ps1")

$repoRoot = Get-RepoRoot
$failed = @()

# --- Backend ------------------------------------------------------------------
if (-not $FrontendOnly) {
    Write-Step "Preparando la base de tests"

    Assert-DockerRunning
    Import-BackendEnv -RepoRoot $repoRoot | Out-Null

    $testDatabaseUrl = Get-TestDatabaseUrl -DevDatabaseUrl $env:DATABASE_URL

    if ($SkipMigrations) {
        Write-Warn2 "Migraciones omitidas (-SkipMigrations)."
    }
    else {
        Invoke-Migrations -RepoRoot $repoRoot -DatabaseUrl $testDatabaseUrl -Label "thers_test"
    }

    Write-Step "pytest (backend)"

    $python = Get-BackendPython -RepoRoot $repoRoot
    Push-Location (Join-Path $repoRoot "backend")
    try {
        $env:TEST_DATABASE_URL = $testDatabaseUrl
        & $python -m pytest @PytestArgs
        if ($LASTEXITCODE -ne 0) {
            $failed += "pytest"
        }
    }
    finally {
        Pop-Location
    }
}

# --- Frontend -----------------------------------------------------------------
if ($Frontend -or $FrontendOnly) {
    Push-Location (Join-Path $repoRoot "Frontend")
    try {
        Write-Step "eslint (frontend)"
        npm run lint
        if ($LASTEXITCODE -ne 0) {
            $failed += "eslint"
        }

        Write-Step "vite build (frontend)"
        npm run build
        if ($LASTEXITCODE -ne 0) {
            $failed += "build"
        }
    }
    finally {
        Pop-Location
    }
}

# --- Resumen ------------------------------------------------------------------
Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "Todas las verificaciones pasaron." -ForegroundColor Green
    Write-Host ""
    exit 0
}

Write-Host ("Fallaron: " + ($failed -join ", ")) -ForegroundColor Red
Write-Host ""
exit 1

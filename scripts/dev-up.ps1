<#
.SYNOPSIS
    Levanta el entorno de desarrollo local completo de THERS.

.DESCRIPTION
    Equivale a los pasos manuales de docs/LOCAL_DEV_SETUP.md seccion 3, en un
    solo comando:

      1. Verifica que Docker, el venv del backend y los .env esten en su lugar.
      2. Levanta PostgreSQL (docker compose) y espera a que este healthy.
      3. Aplica las migraciones a thers_dev y a thers_test.
      4. Abre una ventana para el backend (flask run) y otra para el frontend
         (npm run dev).

    Este script no decide arquitectura ni instala nada: automatiza pasos ya
    documentados. La instalacion inicial (venv, npm ci, .env) sigue siendo
    manual y esta en docs/LOCAL_DEV_SETUP.md seccion 2.

.PARAMETER NoServers
    Solo prepara la infraestructura (base de datos + migraciones). No abre las
    ventanas del backend ni del frontend.

.PARAMETER SkipMigrations
    No aplica migraciones. Util cuando ya se sabe que ambas bases estan al dia.

.PARAMETER BackendOnly
    Abre solo la ventana del backend.

.PARAMETER FrontendOnly
    Abre solo la ventana del frontend (igual levanta la base de datos).

.EXAMPLE
    .\scripts\dev-up.ps1

.EXAMPLE
    .\scripts\dev-up.ps1 -NoServers
#>
[CmdletBinding()]
param(
    [switch]$NoServers,
    [switch]$SkipMigrations,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

. (Join-Path $PSScriptRoot "_lib.ps1")

$repoRoot = Get-RepoRoot

Write-Host ""
Write-Host "THERS - entorno de desarrollo local" -ForegroundColor White
Write-Host "Guia completa: docs/LOCAL_DEV_SETUP.md" -ForegroundColor DarkGray

# --- 1. Verificaciones previas ------------------------------------------------
Write-Step "Verificando requisitos"

Assert-DockerRunning
Write-Ok "Docker responde."

$python = Get-BackendPython -RepoRoot $repoRoot
Write-Ok "Entorno virtual del backend encontrado."

if (-not (Test-Path (Join-Path $repoRoot "Frontend\node_modules"))) {
    Fail "Frontend\node_modules no existe." "Instalar dependencias: cd Frontend; npm ci (docs/LOCAL_DEV_SETUP.md seccion 2.4)."
}
Write-Ok "Dependencias del frontend instaladas."

if (-not (Test-Path (Join-Path $repoRoot ".env"))) {
    Write-Warn2 "No existe el .env de la raiz; docker compose usara POSTGRES_PORT=5432 por defecto."
    Write-Warn2 "Si el puerto de DATABASE_URL no es 5432, copiar .env.example a .env en la raiz."
}

# Carga backend/.env en este proceso. Las ventanas que se abran mas abajo heredan
# estas variables, asi que el backend arranca sin depender de python-dotenv.
Import-BackendEnv -RepoRoot $repoRoot | Out-Null
Write-Ok "Variables de backend/.env cargadas."

# --- 2. Base de datos ---------------------------------------------------------
Write-Step "Levantando PostgreSQL"
Start-Database -RepoRoot $repoRoot

# --- 3. Migraciones -----------------------------------------------------------
$testDatabaseUrl = Get-TestDatabaseUrl -DevDatabaseUrl $env:DATABASE_URL

if ($SkipMigrations) {
    Write-Step "Migraciones omitidas (-SkipMigrations)"
}
else {
    Write-Step "Aplicando migraciones"
    Invoke-Migrations -RepoRoot $repoRoot -DatabaseUrl $env:DATABASE_URL -Label "thers_dev"
    # La base de tests se migra siempre: olvidarla es la causa mas comun de
    # pytest fallando con tablas inexistentes (docs/LOCAL_DEV_SETUP.md seccion 2.3).
    Invoke-Migrations -RepoRoot $repoRoot -DatabaseUrl $testDatabaseUrl -Label "thers_test"
}

# --- 4. Servidores ------------------------------------------------------------
if ($NoServers) {
    Write-Step "Servidores no iniciados (-NoServers)"
}
else {
    Write-Step "Abriendo servidores"

    if (-not $FrontendOnly) {
        $backendCommand = "`$env:FLASK_APP = 'run.py'; & '$python' -m flask run"
        Start-DevWindow -WorkingDirectory (Join-Path $repoRoot "backend") -Command $backendCommand -Title "THERS backend :5000"
    }

    if (-not $BackendOnly) {
        Start-DevWindow -WorkingDirectory (Join-Path $repoRoot "Frontend") -Command "npm run dev" -Title "THERS frontend :5173"
    }
}

# --- Resumen ------------------------------------------------------------------
Write-Host ""
Write-Host "Listo." -ForegroundColor Green
Write-Host "  Frontend    http://localhost:5173"
Write-Host "  Backend     http://127.0.0.1:5000/api"
Write-Host "  PostgreSQL  contenedor thers_postgres_dev (bases thers_dev / thers_test)"
Write-Host ""
Write-Host "  Tests:      .\scripts\dev-test.ps1"
Write-Host "  Apagar:     .\scripts\dev-down.ps1"
Write-Host ""

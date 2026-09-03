# Funciones compartidas por los scripts de arranque local (scripts/dev-*.ps1).
# No se ejecuta suelto: los demas scripts lo cargan con dot-sourcing.
#
# Guia de referencia: docs/LOCAL_DEV_SETUP.md
# Compatible con Windows PowerShell 5.1 (sin operadores ternarios, ?? ni &&).

$ErrorActionPreference = "Stop"

$script:ContainerName = "thers_postgres_dev"
$script:TestDatabaseName = "thers_test"

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "    OK  $Message" -ForegroundColor Green
}

function Write-Warn2 {
    param([string]$Message)
    Write-Host "    !   $Message" -ForegroundColor Yellow
}

function Fail {
    param([string]$Message, [string]$Hint)
    Write-Host ""
    Write-Host "ERROR: $Message" -ForegroundColor Red
    if ($Hint) {
        Write-Host "       $Hint" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}

# Lee un archivo .env y devuelve una hashtable clave -> valor.
# Ignora comentarios, lineas vacias y valores sin definir.
function Read-DotEnvFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }

    foreach ($line in (Get-Content -Path $Path -Encoding UTF8)) {
        if ($line -match '^\s*#') { continue }
        if ($line -notmatch '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=') { continue }

        $parts = $line -split '=', 2
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        # Quita comillas envolventes si las tiene.
        if ($value.Length -ge 2) {
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
        }
        if ($value.Length -gt 0) {
            $values[$key] = $value
        }
    }

    return $values
}

# Carga backend/.env en el proceso actual. Los procesos hijos (las ventanas del
# backend) heredan estas variables, asi que `flask run` funciona sin depender de
# que python-dotenv este instalado (ver docs/LOCAL_DEV_SETUP.md seccion 8).
function Import-BackendEnv {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $envPath = Join-Path $RepoRoot "backend\.env"
    if (-not (Test-Path $envPath)) {
        Fail "No existe backend/.env." "Copiar backend\.env.example a backend\.env (docs/LOCAL_DEV_SETUP.md seccion 2.1)."
    }

    $values = Read-DotEnvFile -Path $envPath
    foreach ($key in $values.Keys) {
        [Environment]::SetEnvironmentVariable($key, $values[$key], "Process")
    }

    if (-not $env:DATABASE_URL) {
        Fail "backend/.env no define DATABASE_URL." "Ver docs/LOCAL_DEV_SETUP.md seccion 2.1."
    }
    if ((-not $env:JWT_SECRET_KEY) -and ($env:ALLOW_INSECURE_JWT_DEV_FALLBACK -ne "1")) {
        Fail "backend/.env no define JWT_SECRET_KEY ni ALLOW_INSECURE_JWT_DEV_FALLBACK=1." "La app no arranca sin una de las dos (backend/app/config.py)."
    }

    return $values
}

# Deriva la cadena de conexion de la base de tests a partir de la de desarrollo,
# reemplazando solo el nombre de la base. Evita duplicar credenciales y puerto en
# dos lugares distintos.
function Get-TestDatabaseUrl {
    param([Parameter(Mandatory = $true)][string]$DevDatabaseUrl)

    if ($env:TEST_DATABASE_URL) {
        return $env:TEST_DATABASE_URL
    }

    $index = $DevDatabaseUrl.LastIndexOf("/")
    if ($index -lt 0) {
        Fail "DATABASE_URL con formato inesperado: no se pudo derivar la base de tests." "Definir TEST_DATABASE_URL a mano."
    }

    return ($DevDatabaseUrl.Substring(0, $index + 1) + $script:TestDatabaseName)
}

function Get-BackendPython {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $python = Join-Path $RepoRoot "backend\venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        Fail "No existe backend\venv (entorno virtual del backend)." "Crearlo: cd backend; python -m venv venv; pip install -r requirements-dev.txt (docs/LOCAL_DEV_SETUP.md seccion 2.3)."
    }
    return $python
}

function Assert-DockerRunning {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Fail "Docker no responde." "Abrir Docker Desktop y esperar a que termine de iniciar."
    }
}

# Levanta el contenedor de PostgreSQL y espera a que el healthcheck pase.
function Start-Database {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [int]$TimeoutSeconds = 90
    )

    Push-Location $RepoRoot
    try {
        docker compose up -d
        if ($LASTEXITCODE -ne 0) {
            Fail "docker compose up -d fallo." "Si el error menciona un puerto ocupado, ajustar POSTGRES_PORT en el .env de la raiz (docs/LOCAL_DEV_SETUP.md seccion 7)."
        }
    }
    finally {
        Pop-Location
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $status = docker inspect --format "{{.State.Health.Status}}" $script:ContainerName
        if ($LASTEXITCODE -eq 0 -and $status -eq "healthy") {
            Write-Ok "PostgreSQL listo ($script:ContainerName)."
            return
        }
        Start-Sleep -Seconds 2
    }

    Fail "PostgreSQL no llego a estado healthy en $TimeoutSeconds segundos." "Revisar: docker compose logs postgres"
}

# Aplica las migraciones de Alembic contra la base indicada.
function Invoke-Migrations {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$DatabaseUrl,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $python = Get-BackendPython -RepoRoot $RepoRoot
    $previousUrl = $env:DATABASE_URL

    Push-Location (Join-Path $RepoRoot "backend")
    try {
        $env:FLASK_APP = "run.py"
        $env:DATABASE_URL = $DatabaseUrl
        & $python -m flask db upgrade
        if ($LASTEXITCODE -ne 0) {
            Fail "flask db upgrade fallo contra $Label." "Verificar que el puerto de DATABASE_URL coincida con POSTGRES_PORT (docs/LOCAL_DEV_SETUP.md seccion 7)."
        }
        Write-Ok "Migraciones aplicadas: $Label"
    }
    finally {
        $env:DATABASE_URL = $previousUrl
        Pop-Location
    }
}

# Abre una ventana nueva de PowerShell ejecutando un comando, heredando las
# variables de entorno ya cargadas en este proceso.
function Start-DevWindow {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$Title
    )

    $full = "`$Host.UI.RawUI.WindowTitle = '$Title'; Set-Location '$WorkingDirectory'; $Command"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $full) | Out-Null
    Write-Ok "Ventana abierta: $Title"
}

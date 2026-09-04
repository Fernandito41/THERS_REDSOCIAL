<#
.SYNOPSIS
    Apaga la base de datos de desarrollo.

.DESCRIPTION
    Por defecto solo detiene el contenedor (docker compose stop): los datos de
    thers_dev y thers_test quedan intactos y vuelven con .\scripts\dev-up.ps1.

    Las ventanas del backend y del frontend no las cierra este script: se cierran
    con Ctrl+C en cada una.

.PARAMETER Remove
    Ademas de detenerlo, elimina el contenedor (docker compose down). El volumen
    de datos se conserva.

.PARAMETER Purge
    DESTRUCTIVO: elimina el contenedor y el volumen de datos. Borra todos los
    usuarios y posts de thers_dev y thers_test. Pide confirmacion escrita.
    Despues de un purge hay que volver a correr las migraciones (dev-up.ps1 ya
    lo hace).

.EXAMPLE
    .\scripts\dev-down.ps1

.EXAMPLE
    .\scripts\dev-down.ps1 -Purge
#>
[CmdletBinding()]
param(
    [switch]$Remove,
    [switch]$Purge
)

. (Join-Path $PSScriptRoot "_lib.ps1")

$repoRoot = Get-RepoRoot
Assert-DockerRunning

Push-Location $repoRoot
try {
    if ($Purge) {
        Write-Host ""
        Write-Host "ATENCION: esto borra el volumen de datos." -ForegroundColor Red
        Write-Host "Se pierden todos los usuarios y posts de thers_dev y thers_test." -ForegroundColor Red
        $answer = Read-Host "Escribir BORRAR para confirmar"
        if ($answer -cne "BORRAR") {
            Write-Host "Cancelado. No se borro nada." -ForegroundColor Yellow
            exit 0
        }

        Write-Step "Eliminando contenedor y volumen"
        docker compose down -v
        if ($LASTEXITCODE -ne 0) {
            Fail "docker compose down -v fallo."
        }
        Write-Ok "Volumen eliminado. Correr .\scripts\dev-up.ps1 para recrear las bases."
    }
    elseif ($Remove) {
        Write-Step "Eliminando contenedor (los datos se conservan)"
        docker compose down
        if ($LASTEXITCODE -ne 0) {
            Fail "docker compose down fallo."
        }
        Write-Ok "Contenedor eliminado."
    }
    else {
        Write-Step "Deteniendo PostgreSQL (los datos se conservan)"
        docker compose stop
        if ($LASTEXITCODE -ne 0) {
            Fail "docker compose stop fallo."
        }
        Write-Ok "Contenedor detenido."
    }
}
finally {
    Pop-Location
}

Write-Host ""

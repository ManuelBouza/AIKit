& {
    $ErrorActionPreference = 'Continue'

    $raiz = Split-Path -Parent $PSScriptRoot

    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: no se encontro 'uv' en el PATH." -ForegroundColor Red
        Write-Host "Instala uv desde https://docs.astral.sh/uv/ y vuelve a ejecutar el script." -ForegroundColor Red
        exit 1
    }

    $pasos = @(
        @{ Nombre = 'uv sync --locked';          Argumentos = @('sync', '--locked') },
        @{ Nombre = 'uv run pytest';             Argumentos = @('run', 'pytest') },
        @{ Nombre = 'uv run ruff check .';       Argumentos = @('run', 'ruff', 'check', '.') },
        @{ Nombre = 'uv run ruff format --check .'; Argumentos = @('run', 'ruff', 'format', '--check', '.') },
        @{ Nombre = 'uv run mypy';               Argumentos = @('run', 'mypy') }
    )

    $resultados = @()

    Push-Location $raiz
    try {
        foreach ($paso in $pasos) {
            Write-Host ""
            Write-Host ("==> {0}" -f $paso.Nombre) -ForegroundColor Cyan
            $codigo = 0
            & uv @($paso.Argumentos)
            $codigo = $LASTEXITCODE
            if ($null -eq $codigo) { $codigo = 0 }
            $resultados += [pscustomobject]@{ Paso = $paso.Nombre; Codigo = [int]$codigo }
        }
    }
    finally {
        Pop-Location
    }

    Write-Host ""
    Write-Host "Resumen de verificaciones" -ForegroundColor Cyan
    foreach ($r in $resultados) {
        $estado = 'OK'
        $color = 'Green'
        if ($r.Codigo -ne 0) {
            $estado = 'ERROR'
            $color = 'Red'
        }
        Write-Host ("{0,-6} {1} (codigo {2})" -f $estado, $r.Paso, $r.Codigo) -ForegroundColor $color
    }

    $fallos = @($resultados | Where-Object { $_.Codigo -ne 0 })
    Write-Host ""
    if ($fallos.Count -gt 0) {
        Write-Host ("ERROR: {0} verificacion(es) fallida(s)." -f $fallos.Count) -ForegroundColor Red
        exit 1
    }

    Write-Host "OK: todas las verificaciones pasaron." -ForegroundColor Green
    exit 0
}

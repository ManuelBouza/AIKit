& {
    $ErrorActionPreference = 'Stop'
    $raiz = Split-Path -Parent $PSScriptRoot
    $paquete = Join-Path $raiz 'packages/aikit-installer'
    $resultados = [System.Collections.Generic.List[object]]::new()

    function Invoke-Control {
        param([string]$Nombre, [string]$Programa, [string[]]$Argumentos, [string]$Directorio)
        Write-Host "`n==> $Nombre" -ForegroundColor Cyan
        $codigo = 1
        $ubicacionCambiada = $false
        try {
            Push-Location -LiteralPath $Directorio
            $ubicacionCambiada = $true
            $global:LASTEXITCODE = 0
            & $Programa @Argumentos | Out-Host
            $codigo = $LASTEXITCODE
            if ($null -eq $codigo) { $codigo = 1 }
        }
        catch {
            Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
            $codigo = 1
        }
        finally { if ($ubicacionCambiada) { Pop-Location } }
        $resultados.Add([pscustomobject]@{ Paso = $Nombre; Codigo = [int]$codigo })
        return ($codigo -eq 0)
    }

    function Add-Omitido {
        param([string]$Nombre)
        $resultados.Add([pscustomobject]@{ Paso = "$Nombre (no ejecutado por fallo previo)"; Codigo = 1 })
    }

    $disponibles = @{}
    foreach ($herramienta in @('uv', 'node', 'npm')) {
        $comando = Get-Command $herramienta -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        $disponibles[$herramienta] = $comando
        if ($null -eq $comando) { Add-Omitido "$herramienta --version (herramienta ausente)" }
        else {
            $versionOk = Invoke-Control "$herramienta --version" $comando.Source @('--version') $raiz
            if (-not $versionOk) { $disponibles[$herramienta] = $null }
        }
    }

    if ($null -ne $disponibles['node']) {
        $nodeCompatible = Invoke-Control 'Node compatible con ESLint 10' $disponibles['node'].Source @('-e', 'const [a,b]=process.versions.node.split(".").map(Number); process.exit((a>=24 || (a===22 && b>=13) || (a===20 && b>=19)) ? 0 : 1)') $raiz
        if (-not $nodeCompatible) { $disponibles['node'] = $null }
    }
    $pythonPreparado = $false
    if ($null -ne $disponibles['uv']) {
        $pythonPreparado = Invoke-Control 'uv sync --locked' $disponibles['uv'].Source @('sync', '--locked') $raiz
    }
    else { Add-Omitido 'uv sync --locked' }
    $nodePreparado = $false
    if ($null -ne $disponibles['node'] -and $null -ne $disponibles['npm']) {
        $nodePreparado = Invoke-Control 'npm ci --include=dev' $disponibles['npm'].Source @('ci', '--include=dev') $paquete
    }
    else { Add-Omitido 'npm ci --include=dev' }

    $controlesPython = @(
        @{ Nombre = 'uv run --no-sync pytest'; Argumentos = @('run', '--no-sync', 'pytest') },
        @{ Nombre = 'uv run --no-sync ruff check .'; Argumentos = @('run', '--no-sync', 'ruff', 'check', '.') },
        @{ Nombre = 'uv run --no-sync ruff format --check .'; Argumentos = @('run', '--no-sync', 'ruff', 'format', '--check', '.') },
        @{ Nombre = 'uv run --no-sync mypy'; Argumentos = @('run', '--no-sync', 'mypy') }
    )
    foreach ($paso in $controlesPython) {
        if ($pythonPreparado) {
            $null = Invoke-Control $paso.Nombre $disponibles['uv'].Source $paso.Argumentos $raiz
        }
        else { Add-Omitido $paso.Nombre }
    }
    foreach ($control in @('typecheck', 'lint', 'format:check', 'test')) {
        if ($nodePreparado) {
            $null = Invoke-Control "npm run $control" $disponibles['npm'].Source @('run', $control) $paquete
        }
        else { Add-Omitido "npm run $control" }
    }

    Write-Host "`nResumen de verificaciones" -ForegroundColor Cyan
    foreach ($resultado in $resultados) {
        $estado = if ($resultado.Codigo -eq 0) { 'OK' } else { 'ERROR' }
        Write-Host ("{0,-6} {1} (codigo {2})" -f $estado, $resultado.Paso, $resultado.Codigo)
    }
    $fallos = @($resultados | Where-Object { $_.Codigo -ne 0 })
    if ($fallos.Count -gt 0) {
        Write-Host "ERROR: $($fallos.Count) verificacion(es) fallida(s)." -ForegroundColor Red
        exit 1
    }
    Write-Host 'OK: todas las verificaciones pasaron.' -ForegroundColor Green
    exit 0
}

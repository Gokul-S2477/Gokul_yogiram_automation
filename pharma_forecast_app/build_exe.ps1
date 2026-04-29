$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$releaseRoot = Join-Path $root ("release_" + $stamp)
$packageRoot = Join-Path $releaseRoot "PharmaForecastApp"
$zipPath = Join-Path $releaseRoot "PharmaForecastApp.zip"

function New-ReleaseZip {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            if (Test-Path $DestinationPath) {
                Remove-Item $DestinationPath -Force
            }
            Compress-Archive -Path "$SourcePath\*" -DestinationPath $DestinationPath -Force
            return
        }
        catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Seconds 4
        }
    }
}

New-Item -ItemType Directory -Path $releaseRoot | Out-Null

& "$root\venv\Scripts\pyinstaller.exe" `
    --clean `
    --noconfirm `
    --distpath "$releaseRoot" `
    --workpath "$root\build" `
    "$root\PharmaForecastApp.spec"

New-ReleaseZip -SourcePath $packageRoot -DestinationPath $zipPath

Write-Host "Build complete:"
Write-Host "Folder: $packageRoot"
Write-Host "Zip:    $zipPath"

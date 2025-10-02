param(
    [switch]$WhatIf
)

# Resolve repo root relative to this script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $scriptDir '..') | Select-Object -ExpandProperty Path
$target = Join-Path $repoRoot 'Backend\.git'

if (-not (Test-Path $target)) {
    Write-Host "No Backend\.git found at: $target"
    exit 0
}

$item = Get-Item -LiteralPath $target -ErrorAction Stop

if ($WhatIf) {
    if ($item.PSIsContainer) {
        Write-Host "[WhatIf] Would remove directory: $target"
    } else {
        Write-Host "[WhatIf] Would remove file: $target"
    }
    exit 0
}

try {
    if ($item.PSIsContainer) {
        Remove-Item -LiteralPath $target -Recurse -Force
        Write-Host "Removed directory: $target"
    } else {
        Remove-Item -LiteralPath $target -Force
        Write-Host "Removed file: $target"
    }
    exit 0
} catch {
    Write-Error "Failed to remove $target : $_"
    exit 1
}

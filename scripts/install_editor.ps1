param(
    [string]$ExpectedSha256 = ""
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root "dist\mod.wh.cpp"
$target = "C:\ProgramData\Windhawk\EditorWorkspace\mod.wh.cpp"
$result = Join-Path $root "dist\install-editor-result.txt"
try {
    if (!(Test-Path -LiteralPath $source)) {
        throw "Generated source missing. Run: python scripts/build.py"
    }
    if (!(Test-Path -LiteralPath $target)) {
        throw "Windhawk editor source not found: $target"
    }
    $current = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    $desired = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    if ($ExpectedSha256 -and $current -ne $ExpectedSha256 -and $current -ne $desired) {
        throw "Windhawk editor source changed unexpectedly; refusing overwrite"
    }
    if ($current -ne $desired) {
        $backupName = "editor-backup-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".wh.cpp"
        $backup = Join-Path (Join-Path $root "dist") $backupName
        Copy-Item -LiteralPath $target -Destination $backup -ErrorAction Stop
        Copy-Item -LiteralPath $source -Destination $target -Force -ErrorAction Stop
    }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $desired) {
        throw "Checksum mismatch after installing Windhawk source"
    }
    Set-Content -LiteralPath $result -Value "SUCCESS" -Encoding UTF8
    Write-Host "Windhawk editor source installed. Reopen the editor and compile."
}
catch {
    Set-Content -LiteralPath $result -Value ("ERROR: " + $_.Exception.Message) -Encoding UTF8
    throw
}

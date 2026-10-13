$ErrorActionPreference = "Stop"
$archive = Join-Path $env:RUNNER_TEMP "windhawk-compiler-1.6.7z"
$folder = Join-Path $env:RUNNER_TEMP "windhawk-compiler-1.6"
$uri = "https://github.com/ramensoftware/windhawk-dependencies/releases/download/v1.6/windhawk-compiler-1.6.7z"
Invoke-WebRequest -Uri $uri -OutFile $archive
$sevenZip = "C:\Program Files\7-Zip\7z.exe"
if (!(Test-Path $sevenZip)) { throw "7-Zip not installed on Windows GitHub runner" }
New-Item -ItemType Directory -Force -Path $folder | Out-Null
& $sevenZip x $archive "-o$folder" -y
if ($LASTEXITCODE -ne 0) { throw "Windhawk compiler extraction failed" }
$clang = Get-ChildItem -Path $folder -Recurse -Filter clang++.exe -File |
    Select-Object -First 1
if (!$clang) { throw "Windhawk Clang executable missing" }
$binFolder = Split-Path -Parent $clang.FullName
$toolchainRoot = Split-Path -Parent $binFolder
if (!(Test-Path (Join-Path $toolchainRoot "include\winrt\Windows.Foundation.h"))) {
    throw "WinRT headers missing from compiler"
}
Add-Content -LiteralPath $env:GITHUB_ENV -Value "WINDHAWK_COMPILER_ROOT=$toolchainRoot"
Write-Host "Windhawk Clang toolchain ready: $toolchainRoot"

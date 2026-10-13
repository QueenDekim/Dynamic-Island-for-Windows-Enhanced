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
# Windhawk ships the C++/WinRT projection separately from clang.
# Include the official merged headers used by Windhawk 1.6.
$winrtArchive = Join-Path $env:RUNNER_TEMP "windhawk-winrt.7z"
$winrtUrl = "https://github.com/ramensoftware/windhawk-dependencies/releases/download/v1.6/winrt_winui2_2.8.7_winui3_1.7.250401001.7z"
Invoke-WebRequest -Uri $winrtUrl -OutFile $winrtArchive
$winrtDir = Join-Path $toolchainRoot "include\winrt"
New-Item -ItemType Directory -Force -Path $winrtDir | Out-Null
& $sevenZip x $winrtArchive "-o$winrtDir" -y
if ($LASTEXITCODE -ne 0) { throw "WinRT header extraction failed" }
if (!(Test-Path (Join-Path $winrtDir "Windows.Foundation.h")) -or
    !(Test-Path (Join-Path $winrtDir "Windows.Media.Control.h"))) {
    throw "C++/WinRT system projection headers missing"
}
Add-Content -LiteralPath $env:GITHUB_ENV -Value "WINDHAWK_COMPILER_ROOT=$toolchainRoot"
Write-Host "Windhawk Clang toolchain ready: $toolchainRoot"

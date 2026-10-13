$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$toolchain = if ($env:WINDHAWK_COMPILER_ROOT) {
    $env:WINDHAWK_COMPILER_ROOT
} else {
    "C:\Program Files\Windhawk\Compiler"
}
$clang = Join-Path $toolchain "bin\clang++.exe"
$include = Join-Path $toolchain "include"
if (!(Test-Path -LiteralPath $clang)) { throw "Windhawk clang++ missing: $clang" }
$flags = @(
    '-x', 'c++', '-std=c++23', '-target', 'x86_64-w64-mingw32',
    '-DUNICODE', '-D_UNICODE', '-DWINVER=0x0A00',
    '-D_WIN32_WINNT=0x0A00', '-D_WIN32_IE=0x0A00',
    '-DNTDDI_VERSION=0x0A000008', '-D__USE_MINGW_ANSI_STDIO=0',
    '-DWH_MOD', '-DWH_EDITING',
    '-include', 'windhawk_api.h',
    "-I$(Join-Path $root 'preview\include')",
    "-I$include",
    '-DDYNAMIC_ISLAND_PREVIEW=1', '-O1',
    '-ffunction-sections', '-fdata-sections'
)
$out = Join-Path $root "dist\real-preview.exe"
$source = Join-Path $PSScriptRoot "preview.cpp"
$argsList = @(
    $flags + @(
        $source, '-o', $out, '-Wl,--gc-sections',
        '-static-libgcc', '-static-libstdc++',
        '-ld2d1', '-ldwrite', '-lwindowscodecs', '-lgdi32',
        '-luser32', '-lkernel32', '-lole32', '-loleaut32',
        '-luuid', '-ldwmapi', '-lshell32', '-lshcore', '-lsetupapi',
        '-lwinhttp', '-lpdh', '-lwinmm', '-ladvapi32', '-lcomctl32',
        '-lpropsys', '-lavrt', '-lws2_32', '-lruntimeobject'
    )
)
& $clang @argsList
if ($LASTEXITCODE -ne 0) { throw "Native Direct2D preview build failed" }
Write-Host "REAL_PREVIEW_EXE=$out"

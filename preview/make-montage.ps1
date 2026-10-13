param([string]$Directory = "")
$ErrorActionPreference = "Stop"
if (!$Directory) { $Directory = Join-Path (Split-Path -Parent $PSScriptRoot) "previews" }
Add-Type -AssemblyName System.Drawing
$names = @("media-v2","discord-voice","calendar","gamebar-v2",
           "hardware-monitor","notification","weather-v2","compact-media")
$width=1140
$height=920
$canvas=New-Object System.Drawing.Bitmap($width,$height)
$draw=[System.Drawing.Graphics]::FromImage($canvas)
try {
    $draw.Clear([System.Drawing.Color]::FromArgb(11,9,17))
    $draw.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    for($i=0;$i -lt $names.Count;$i++){
        $src=Join-Path $Directory ($names[$i]+".png")
        if(!(Test-Path -LiteralPath $src)){throw "Native preview missing: $src"}
        $img=[System.Drawing.Image]::FromFile($src)
        try {
            $col=$i % 2
            $row=[Math]::Floor($i/2)
            $cellX=22+$col*560
            $cellY=16+$row*226
            $scale=[Math]::Min(520/$img.Width,204/$img.Height)
            $w=[int]($img.Width*$scale)
            $h=[int]($img.Height*$scale)
            $x=$cellX+[int]((520-$w)/2)
            $y=$cellY+[int]((204-$h)/2)
            # Only composite REAL Renderer::Render screenshots.
            $draw.DrawImage($img,$x,$y,$w,$h)
        } finally { $img.Dispose() }
    }
    $output=Join-Path $Directory "Full-preview-v2.png"
    $canvas.Save($output,[System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "NATIVE_MONTAGE=$output"
} finally {
    $draw.Dispose()
    $canvas.Dispose()
}

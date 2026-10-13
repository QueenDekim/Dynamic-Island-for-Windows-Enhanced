"""Validate the Windhawk editor metadata, embedded README, and module help."""
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
source=(root/"src/mod.wh.cpp").read_text(encoding="utf-8")
standalone=root/"dist/mod.wh.cpp"
expected={
    "id":"dynamic-island-for-windows-enhanced",
    "name":"Dynamic Island for Windows Enhanced",
    "version":"1.4.0",
    "github":"https://github.com/QueenDekim",
    "license":"MIT",
    "include":"windhawk.exe",
}
assert source.count("// ==WindhawkMod==")==1
assert source.count("// ==/WindhawkMod==")==1
assert source.count("// ==WindhawkModReadme==")==1
assert source.count("// ==/WindhawkModReadme==")==1
assert source.count("// ==WindhawkModSettings==")==1

metadata=source.split("// ==WindhawkMod==",1)[1].split("// ==/WindhawkMod==",1)[0]
meta=dict(re.findall(r"(?m)^// @([a-zA-Z]+)\s+([^\r\n]+)",metadata))
for field,value in expected.items():
    assert meta.get(field)==value,(field,meta.get(field),value)
assert "media and browser playback" in meta["description"]
assert "Discord voice" in meta["description"]
assert "game overlay" in meta["description"]
assert "DekimDev" in meta["author"] and "Himanshu" in meta["author"]
assert meta.get("compilerOptions","").startswith("-lole32 ")
assert "-lwindowscodecs" in meta["compilerOptions"]

readme=source.split("// ==WindhawkModReadme==",1)[1].split("// ==/WindhawkModReadme==",1)[0]
assert readme.startswith("\n/*\n# Dynamic Island for Windows Enhanced\n")
assert readme.endswith("\n*/\n")
assert readme.count("*/")==1
for term in (
    "Renderer::Render()", "Discord voice", "WASAPI Process Loopback",
    "Auto Game Mode overlay", "Browser Media", "Native Messaging",
    "elapsed/total", "GitHub Issues", "Himanshu", "DekimDev",
    "Ctrl+Alt+D", "Game Overlay", "MIT license",
):
    assert term in readme, term
assert "devcode90/Dynamic-Island-for-Windows/793cf954" not in readme
assert "ramensoftware/windhawk-mods/issues" not in readme
assert "dynamic-island-for-windows issues" not in readme
assert "Dynamic Island for Windows\n\n" not in readme
urls=re.findall(r"https://raw\.githubusercontent\.com/QueenDekim/Dynamic-Island-for-Windows-Enhanced/main/previews/([\w-]+\.png)",readme)
assert len(urls)==7 and len(set(urls))==7,urls
for filename in urls:
    assert (root/"previews"/filename).is_file(),filename

for setting,description_fragment in {
    "Discord":"Discord tab within the main island",
    "Media":"elapsed/total time",
    "HardwareMonitorModule":"CPU, GPU, RAM, disk and network",
    "GameOverlayShowFps":"not the game's engine FPS",
    "Weather":"expanded weather dashboard",
    "AutoGameOverlay":"Automatically show Game Overlay",
}.items():
    pattern=rf"(?m)^  - {setting}:\s*[^\r\n]*\n(?:[^\n]*\n){{0,2}}"
    found=re.search(pattern,source)
    assert found and description_fragment in found.group(0),(setting,found.group(0) if found else "")

if standalone.is_file():
    bundle=standalone.read_text(encoding="utf-8")
    assert bundle.startswith(source[:source.index("// ==/WindhawkModReadme==")+len("// ==/WindhawkModReadme==")]), \
        "Generated Windhawk bundle metadata/readme differs from core source"

print("WINDHAWK_METADATA_AND_README_OK")
print("NATIVE_README_IMAGES="+str(len(urls)))

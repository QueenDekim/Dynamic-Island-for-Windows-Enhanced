"""Validate genuine, full-coverage Direct2D outputs without Pillow."""
from __future__ import annotations
from pathlib import Path
import re
import struct

root=Path(__file__).resolve().parents[1]
images=root/"previews"
source=(root/"src/mod.wh.cpp").read_text(encoding="utf-8")
native=(root/"preview/preview.cpp").read_text(encoding="utf-8")
readme=(root/"README.md").read_text(encoding="utf-8")
assert '#include "../dist/mod.wh.cpp"' in native
assert "renderer.Render(state,settings,activity" in native
assert "renderer.SavePreviewPng(" in native
assert "DYNAMIC_ISLAND_PREVIEW" in source
assert "CreateDCRenderTarget" in source and "SavePreviewPng" in source
assert not (root/"scripts/render_previews.py").exists()
assert not (root/"tests/test_previews.py").exists()

kinds=set(re.findall(r"^\s*(\w+)\s*,?\s*$",
    re.search(r"enum class IslandKind\s*\{([^}]+)\}",source,re.S).group(1),re.M))
required={
    "Idle":"idle-v2","Media":"media-v2","Progress":"progress",
    "Clipboard":"clipboard","Notification":"notification","Volume":"volume",
    "BatteryLow":"battery-low","CapsLock":"caps-lock","Device":"device",
    "Bluetooth":"bluetooth","Timer":"timer","DoNotDisturb":"dnd",
    "Discord":"discord-voice","Split":"discord-voice-compact"}
assert required.keys() == kinds,(required.keys()-kinds,kinds-required.keys())
scenes=set(re.findall(r'\{L"([a-z0-9-]+)"\s*,\s*IslandKind::',native))
assert set(required.values())<=scenes
pngs={x.stem:x for x in images.glob("*.png")}
assert set(scenes)<=set(pngs),set(scenes)-set(pngs)
assert set(pngs)==set(scenes)|{"Full-preview-v2"},(set(pngs)-scenes,scenes-set(pngs))
for label,filename in pngs.items():
    content=filename.read_bytes()
    assert content[:8]==b"\x89PNG\r\n\x1a\n",filename
    width,height=struct.unpack(">II",content[16:24])
    assert width>=105 and height>=75 and len(content)>750,label
    assert b"IDAT" in content,label
refs=set(re.findall(r'previews/([a-zA-Z0-9-]+\.png)',readme))
assert refs and refs<={p.name for p in pngs.values()},refs-{p.name for p in pngs.values()}
for title in ["### Dashboards","### Hardware Monitor","### Themes","### Privacy Indicators"]:
    assert title in readme,title
assert readme.index("### Dashboards")<readme.index("### Hardware Monitor")<readme.index("### Themes")<readme.index("### Privacy Indicators")
assert "render_previews.py" not in readme
print(f"REAL_D2D_PREVIEWS_VALIDATED={len(pngs)} island_kinds={len(kinds)} readme_images={len(refs)}")

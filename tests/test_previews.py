"""Verify every island kind and README image has a generated synthetic preview."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
from PIL import Image

root=Path(__file__).resolve().parents[1]
cpp=(root/"src/mod.wh.cpp").read_text(encoding="utf-8")
readme=(root/"README.md").read_text(encoding="utf-8")
preview=root/"previews"
manifest=json.loads((preview/"preview-manifest.json").read_text(encoding="utf-8"))
assert manifest["type"].startswith("synthetic preview"), "Never mislabel mockups as screenshots"
kinds=re.search(r"enum class IslandKind\s*\{([^}]+)\}",cpp,re.S)
assert kinds, "IslandKind enum not found"
expected={x.strip().split("=")[0].strip() for x in kinds.group(1).split(",") if x.strip()}
mapping=manifest["island_kinds"]
assert expected == set(mapping), (expected-set(mapping),set(mapping)-expected)
print("PASS IslandKind mapping:",", ".join(sorted(expected)))
files=manifest["files_sha256"]
assert len(files) >= 30 and "Full-preview-v2.png" in files, "Incomplete dashboard gallery"
for name,digest in files.items():
    file=preview/name
    assert file.is_file(), f"Missing image: {name}"
    assert hashlib.sha256(file.read_bytes()).hexdigest()==digest, f"Outdated manifest {name}"
    with Image.open(file) as im:
        assert im.format == "PNG" and im.width>=500 and im.height>=200, name
        im.verify()
for kind,name in mapping.items():
    assert name+".png" in files, f"Missing mapped image: {kind}"
refs=set(re.findall(r'previews/([A-Za-z0-9-]+\.png)',readme))
assert len(refs) >= 20, f"README gallery references just {len(refs)} previews"
assert refs <= set(files), f"Broken README previews: {refs-set(files)}"
for section in ("## 📸 See it in Action", "### Dashboards",
                "### Hardware Monitor", "### Themes", "### Privacy Indicators"):
    assert section in readme, f"Missing original README preview section: {section}"
assert readme.index("### Dashboards") < readme.index("### Hardware Monitor") < readme.index("### Themes") < readme.index("### Privacy Indicators")
assert 'g_state.system.renderFps = measured;' in cpp
assert 'if (elapsed >= 1.0)' in cpp
assert 'g_state.system.renderFps = ClampInt(static_cast<int>(1.0f / std::max(dt' not in cpp
print("PASS FPS value sampled no more than once per second")
print(f"PASS {len(files)} PNG previews and {len(refs)} README image references")

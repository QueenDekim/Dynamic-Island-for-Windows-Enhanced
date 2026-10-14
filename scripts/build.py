"""Build a standalone Windhawk source from the core + two Git submodules.

Windhawk's editor cannot resolve repository-local includes after copying a
single .cpp into ProgramData. This intentionally inlines only three owned
bridge headers, preserving all Windhawk metadata and other SDK includes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "mod.wh.cpp"
OUTPUT = ROOT / "dist" / "mod.wh.cpp"
LOCAL_HEADERS = {
    "../integrations/browser-media/windhawk/browser_media_bridge.h",
    "../integrations/discord/windhawk/discord_bridge.h",
    "discord_process_loopback.h",
    "game_detection.h",
}
INCLUDE = re.compile(r'(?m)^#include "([^"]+)"[ \t]*\r?$')
dependencies: list[Path] = []


def inline_headers(path: Path, stack: tuple[Path, ...] = ()) -> str:
    resolved = path.resolve(strict=True)
    if resolved in stack:
        raise RuntimeError(f"Circular local include: {resolved}")
    contents = resolved.read_text(encoding="utf-8-sig")
    if resolved != SOURCE.resolve():
        # Header guards apply only to separate translation units. Removing
        # them from the flattened editor source also avoids Clang warnings.
        contents = re.sub(r"(?m)^[ \t]*#pragma once[ \t]*\r?\n?", "", contents)
    dependencies.append(resolved)

    def replace(match: re.Match[str]) -> str:
        ref = match.group(1)
        if ref not in LOCAL_HEADERS:
            return match.group(0)
        target = (resolved.parent / ref).resolve(strict=True)
        if not target.is_relative_to(ROOT):
            raise RuntimeError(f"Include escaped repository: {ref}")
        return (
            f"\n// BEGIN inlined Git submodule: {target.relative_to(ROOT).as_posix()}\n"
            + inline_headers(target, stack + (resolved,))
            + f"\n// END inlined Git submodule: {target.relative_to(ROOT).as_posix()}\n"
        )

    return INCLUDE.sub(replace, contents)


def main() -> int:
    for name in ("browser-media", "discord"):
        if not (ROOT / "integrations" / name / ".git").exists():
            print(f"Missing Git submodule: integrations/{name}", file=sys.stderr)
            print("Run: git submodule update --init --recursive", file=sys.stderr)
            return 2
    built = inline_headers(SOURCE)
    if not built.startswith("// ==WindhawkMod=="):
        raise RuntimeError("Windhawk metadata was lost")
    if built.count("std::array<float, 8> DIDiscordIsolatedAudioLevels(bool inCall)") != 1:
        raise RuntimeError("Discord process-isolated audio integration is missing")
    if "C:/Projects/DynamicIsland" in built:
        raise RuntimeError("Bundled source contains a developer-specific include")
    if INCLUDE.search(built) and any(
        match.group(1) in LOCAL_HEADERS for match in INCLUDE.finditer(built)
    ):
        raise RuntimeError("Local bridge header was not inlined")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(built, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    info = {
        "source": "src/mod.wh.cpp",
        "bundle": "dist/mod.wh.cpp",
        "sha256": digest,
        "sources": [str(p.relative_to(ROOT)).replace("\\", "/") for p in dependencies],
    }
    (OUTPUT.parent / "manifest.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("BUILT", OUTPUT)
    print("SHA256", digest)
    print("BUNDLED_FILES", len(dependencies))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

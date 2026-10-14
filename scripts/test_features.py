"""Integration invariants for the Windhawk source + Discord transport."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / "src/mod.wh.cpp").read_text(encoding="utf-8")
bridge = (root / "integrations/discord/windhawk/discord_bridge.h").read_text(encoding="utf-8")
agent = (root / "integrations/discord/agent/agent.py").read_text(encoding="utf-8")
voice = (root / "integrations/discord/agent/voice_state.py").read_text(encoding="utf-8")

def check(value: bool, description: str) -> None:
    if not value:
        raise AssertionError(description)
    print("PASS", description)

check("formatCompactTime(elapsedSeconds) + L\"/\" + formatCompactTime(totalSeconds)"
      in source, "compact media uses elapsed/total timeline")
check("activity.width = 198.0f;" in source,
      "compact media reserves room for timeline")
check("g_discordProcessRunning.load" in source and
      "if (!settings.discord || !g_discordProcessRunning.load" in source,
      "Discord tab requires enabled module and running desktop process")
check(source.count("if (voiceTabSecond) activeTabs.push_back(5);") == 2,
      "voice tab inserted second in idle and media dashboards")
check(source.count("if (showDiscord && !voiceTabSecond) activeTabs.push_back(5);") == 2,
      "Discord tab moves to end when not on a call")
check("return 1;" in source.split("int DiscordTabIndex",1)[1].split("}",1)[0],
      "click hit-test index matches second voice tab")
check("g_discordAutoExpandUntil" in source and
      "now < g_discordAutoExpandUntil.load" in source and
      "recentTrackChange || recentDiscordChange" in source,
      "voice join/switch triggers transient auto-expand")
check("update.channelId != previous.channelId" in bridge and
      "g_discordAutoExpandUntil.store(NowSeconds() + 5.0" in bridge,
      "voice transitions compare stable channel IDs")
check('lines.append(field(state.get("channel_id", "")))' in voice,
      "agent writes channel IDs to the extended wire format")
check("output->icon = DIDiscordReadImage(DIBBridgeUtf8(lines[5]));" in bridge,
      "Discord notification uses sender avatar asset")
check('publish_notification(evt.get("data", {}), ASSETS)' in agent,
      "Discord agent downloads sender avatar for notifications")
check("DIDiscordIsolatedAudioLevels(activeCall)" in bridge,
      "Discord continues using isolated process audio")
detector = (root / "src/game_detection.h").read_text(encoding="utf-8")
bundle_script = (root / "scripts/build.py").read_text(encoding="utf-8")
check("AutoGameOverlay: false" in source and
      'Wh_GetIntSetting(L"Modules.AutoGameOverlay")' in source,
      "opt-in Auto Game Mode Windhawk setting")
check("g_autoGameOverlayActive.exchange(" in source and
      "DIIsForegroundGame(hwnd, IsForegroundFullscreen(hwnd))" in source,
      "foreground game detection runs on the overlay thread")
check("kinds.assign(1, IslandKind::Idle)" in source and
      "if (IsGameOverlayActive(g_settings))" in source,
      "game overlay overrides media without changing manual settings")
check("!IsGameOverlayActive(g_settings)" in source and
      "g_settings.autoHideFullscreen" in source,
      "full-screen game overlay is not suppressed")
check("g_settings.autoGameOverlay ? 1000 : INFINITE" in source,
      "auto-park wakes to detect games without busy polling")
check("DIWindowsRecordedGamePath" in detector and
      "DIKnownGameModule" in detector and "DIKnownGameLocation" in detector,
      "game detection covers Windows registry, engine modules and storefronts")
check("game_detection.h" in bundle_script,
      "standalone Windhawk bundle includes the game detector")
print("FEATURE_INVARIANTS_OK")

"""Guard against synthesized Discord bars and local-only time preference."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
cpp=(root/"src/mod.wh.cpp").read_text(encoding="utf-8")
capture=(root/"integrations/discord/windhawk/discord_process_loopback.h").read_text(encoding="utf-8")
bridge=(root/"integrations/discord/windhawk/discord_bridge.h").read_text(encoding="utf-8")
assert "std::array<float, 8> DIDiscordIsolatedAudioLevels(bool inCall)" in capture
assert "const double left = pcm[i * 2] / 32768.0;" in capture
assert "const double right = pcm[i * 2 + 1] / 32768.0;" in capture
assert "DIDiscordIsolatedAudioLevels(activeCall)" in bridge
assert "voice.waveform[slot] = level > previous" in bridge
assert "voice.waveform[static_cast<size_t>(i)]" in cpp
assert "std::sin(phase + static_cast<float>(i)" not in cpp
assert "int64_t voiceStartedUnix = 0" in cpp
assert "voice.voiceStartedUnix > 0 ? voice.voiceStartedUnix : voice.joinedUnix" in cpp
assert "next->voiceStartedUnix" in bridge
print("DISCORD_PCM_VISUALIZER_AND_SESSION_TIMER_OK")

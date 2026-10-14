"""Regression: only the selected browser process may feed the Media waveform."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/"src/mod.wh.cpp").read_text(encoding="utf-8")
bridge=(root/"integrations/browser-media/windhawk/browser_media_bridge.h").read_text(encoding="utf-8")
page=(root/"integrations/browser-media/extension/page-media.js").read_text(encoding="utf-8")
worker=(root/"integrations/browser-media/extension/background.js").read_text(encoding="utf-8")
host=(root/"integrations/browser-media/native/host.py").read_text(encoding="utf-8")
required=(
    "BOOL CALLBACK DIBrowserAudioWindowEnumProc(HWND window, LPARAM arg)",
    "EnumWindows(DIBrowserAudioWindowEnumProc, reinterpret_cast<LPARAM>(&search))",
    "DWORD WINAPI BrowserAudioThreadProc(void*)",
    "DIDiscordProcessCapture processCapture",
    "g_browserAudioCaptureNeeded.store(",
    "snapshot.media.browserBridge ||",
    "browserMediaForIsolatedCapture && !snapshot.media.browserMediaMuted",
    "mediaWaveformVisible && mediaHasAttributableAudio",
    "!snapshot.media.browserBridge &&",
    "g_state.waveform.fill(0.0f)",
    "if (state.media.browserMediaMuted) return;",
    "g_browserAudioThread = CreateThread(",
)
for term in required:
    assert term in source, term
assert "EnumWindows([]" not in source
for text,token in (
    (bridge, 'next.browserMediaMuted = lines.size() >= 10 && lines[9] == "1"'),
    (page, "audioMuted: media.muted || media.volume <= 0"),
    (worker, "audioMuted: data.audioMuted === true"),
    (host, '"1" if message.get("audioMuted") is True else "0"'),
):
    assert token in text, token

def flags(visible, browser, fallback, bridge_active, muted):
    global_capture = visible and not bridge_active and not fallback and not browser
    browser_capture = visible and (bridge_active or (browser and not fallback)) and not muted
    return global_capture, browser_capture
assert flags(True,True,True,True,False)==(False,True)
assert flags(True,True,True,True,True)==(False,False)
assert flags(True,True,False,False,False)==(False,True)
assert flags(True,True,False,False,True)==(False,False)
assert flags(True,False,False,False,False)==(True,False)
assert flags(False,True,True,True,False)==(False,False)
print("BROWSER_PROCESS_AUDIO_ISOLATION_OK")

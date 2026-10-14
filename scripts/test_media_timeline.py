"""Regression checks for the browser media timer reconciliation."""
from pathlib import Path

source=(Path(__file__).resolve().parents[1]/"src"/"mod.wh.cpp").read_text(encoding="utf-8")
for token in (
    "const int64_t predicted = g_state.media.positionTicks +",
    "constexpr int64_t kSampleJitterTicks = 20000000",
    "std::clamp(error, int64_t{0}, int64_t{750000})",
    "next.playing && g_state.media.playing",
    "next.endTicks == g_state.media.endTicks",
):
    assert token in source, token

def reconcile(previous, sample, dt_ms, same_track=True, both_playing=True):
    if not same_track or not both_playing:
        return sample
    predicted = previous + dt_ms*10_000
    error = sample-predicted
    if -20_000_000 <= error <= 20_000_000:
        return predicted+max(0,min(error,750_000))
    return sample

start=70_000_000
# One-second-old browser position may not cause a timer rewind.
assert reconcile(start, start+6_000_000,1500) == start+15_000_000
# Tiny ahead-of-renderer discrepancies are corrected only gradually.
assert reconcile(start, start+15_900_000,1500) == start+15_750_000
# Real backward and forward seeks are not filtered out.
assert reconcile(start,start-50_000_000,1500)==start-50_000_000
assert reconcile(start,start+150_000_000,1500)==start+150_000_000
# Pauses, track changes and explicit restarts use the browser's real position.
assert reconcile(start,start+600_000,1500,both_playing=False)==start+600_000
assert reconcile(start,start+600_000,1500,same_track=False)==start+600_000
position=start
for n in range(24):
    sample=position + 7_000_000  # transport latency, 0.8sec behind predicted
    new=reconcile(position,sample,1500)
    assert new >= position+15_000_000
    position=new
print("BROWSER_MEDIA_TIMER_SYNC_OK")

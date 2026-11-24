"""Timing for the narration you record yourself.

Each narration segment gets a time slot from its word count, at a relaxed
speaking pace. scenes.py starts the visuals for segment i at the start of its
slot, so if you read the script (narration.py / Script_with_timestamps.pdf)
at a natural pace, your voice lines up with the animation.

Change WORDS_PER_SEC to speed up / slow down the whole video, then re-render.
"""
from narration import NARRATION, SCENE_ORDER

WORDS_PER_SEC = 2.5      # about 150 words per minute
LEAD, GAP, TAIL = 0.6, 0.7, 1.0          # seconds of breathing room
EXTRA_TAIL = {"S0_Title": 1.5, "S7_Summary": 8.0}   # time to read title / credits


def seg_duration(text):
    words = len(text.split())
    pauses = text.count(".") + text.count("?") + text.count(":")   # sentence breaks
    return words / WORDS_PER_SEC + 0.2 * pauses


def scene_timings(scene):
    t, segs = LEAD, []
    for i, text in enumerate(NARRATION[scene]):
        d = seg_duration(text)
        segs.append({"start": t, "dur": d})
        t += d + (GAP if i < len(NARRATION[scene]) - 1 else 0)
    t += TAIL + EXTRA_TAIL.get(scene, 0.0)
    return {"segments": segs, "total": t}


TIMINGS = {s: scene_timings(s) for s in SCENE_ORDER}

if __name__ == "__main__":
    clock = 0.0
    for s in SCENE_ORDER:
        print(f"{s:20s} starts {int(clock//60)}:{clock%60:04.1f}  length {TIMINGS[s]['total']:5.1f}s")
        clock += TIMINGS[s]["total"]
    print(f"TOTAL {int(clock//60)}:{clock%60:04.1f}")

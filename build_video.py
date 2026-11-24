"""Render every scene at 1080p30 and join them into one MP4.

    python build_video.py                        # all scenes
    python build_video.py --scenes S0_Title S7_Summary   # re-render some, then re-join

Output: ../GaussianElimination_Video.mp4 (silent track, ready for your voice-over)
        build/cues/*.json  -> exact start time of each narration cue
Then run make_script_pdf.py to refresh the timestamped narration script.

Adding your recorded narration afterwards (one file, any format):
    ffmpeg -i GaussianElimination_Video.mp4 -i my_voice.m4a -map 0:v -map 1:a \
           -c:v copy -c:a aac -b:a 192k -shortest GaussianElimination_Video_final.mp4
"""
import argparse
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

from narration import SCENE_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "build", "media")
OUT = os.path.join(os.path.dirname(HERE), "GaussianElimination_Video.mp4")


def render(scene):
    cmd = ["manim", "-qh", "--fps", "30", "--disable_caching", "--media_dir", MEDIA,
           os.path.join(HERE, "scenes.py"), scene]
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit(f"render failed: {scene}")
    print("rendered", scene, flush=True)


def join():
    vids = [os.path.join(MEDIA, "videos", "scenes", "1080p30", s + ".mp4") for s in SCENE_ORDER]
    lst = os.path.join(HERE, "build", "concat.txt")
    with open(lst, "w") as f:
        for v in vids:
            f.write(f"file '{v}'\n")
    joined = os.path.join(HERE, "build", "joined.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", joined], check=True)
    # add a silent stereo track so every player/uploader treats it as a normal video
    tmp = OUT[:-4] + ".part.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", joined,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    shutil.move(tmp, OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", nargs="*", default=SCENE_ORDER)
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(render, a.scenes))
    join()

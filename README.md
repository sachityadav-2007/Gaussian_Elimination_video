# Gaussian Elimination: solving a 3 × 3 system — M3 Animation Video

**Concept:** Gaussian elimination (Linear Algebra topic bank)
**Student:** Sachit Kumar · URN E25B070503
**Video:** `GaussianElimination_Video.mp4` (1920×1080, 16:9, 30 fps, about 5 minutes)

**Learning objective:** By the end of this video, the viewer will be able to carry out Gaussian
elimination on a 3 × 3 system, highlighting pivots and row operations to reach row echelon form,
and explain why row operations never change the solution set.

## Repository contents

| Path | What it is |
|---|---|
| `GaussianElimination_Video.mp4` | Final video |
| `Storyboard.pdf` | 6-scene storyboard: purpose, visual plan, maths, narration and stills for each scene |
| `Script_with_timestamps.pdf` | Voice-over script with the exact time each line starts |
| `Code/scenes.py` | All Manim scenes (one class per scene) |
| `Code/narration.py` | Narration script, split into cues |
| `Code/timing.py` | Gives each cue a time slot so the visuals line up with the narration |
| `Code/config.py` | Student name and ID shown on the opening and closing frames |
| `Code/build_video.py` | Renders every scene at 1080p and joins them into the MP4 |
| `Code/make_docs.py` | Builds `Storyboard.pdf` and `Script_with_timestamps.pdf` from the render |
| `Code/verify_math.py` | Checks every number shown in the video with exact fractions |
| `Code/requirements.txt` | Python packages |

## The example used

```
 x +  y +  z = 6          R2 ← R2 − 2R1   →  [0  1 −1 | −1]
2x + 3y +  z = 11         R3 ← R3 −  R1   →  [0 −2  1 | −1]
 x −  y + 2z = 5          R3 ← R3 + 2R2   →  [0  0 −1 | −3]

Back substitution:  z = 3,  y = −1 + 3 = 2,  x = 6 − 2 − 3 = 1   →  (x, y, z) = (1, 2, 3)
```

2D intuition: `x + y = 3` and `2x − y = 0` meet at (1, 2). The operation `R2 ← R2 − 2R1` gives `−3y = −6`.
The animation rotates the line through the family `(2 − 2t)x + (−1 − 2t)y = −6t`, `0 ≤ t ≤ 1`, which
passes through (1, 2) for every t. That is why the intersection never moves.

## Video structure

| # | Scene (class) | Purpose |
|---|---|---|
| — | `S0_Title` | Opening frame: title, concept, name, ID |
| 1 | `S1_Hook` | Three equations = three planes in 3D; where do they meet? |
| 2 | `S2_Concept` | Ax = b, augmented matrix, the 3 row operations, row echelon form, learning objective |
| 3 | `S3_Intuition` | 2D: a replacement operation rotates a line about the same intersection point |
| 4 | `S4_Elimination`, `S5_BackSub` | Worked example: pivots, multipliers, entry-by-entry arithmetic, back substitution, check |
| 5 | `S6_Interpretation` | Planes morph to the eliminated system around a fixed point; unique / none / infinite cases |
| 6 | `S7_Summary` | Closing frame: 3 takeaways, references, music statement, AI disclosure |

Colour code: **yellow** pivots · **orange** multiplier / row operation · **blue** row being changed ·
**green** new zeros and results · equations 1/2/3 drawn in blue/green/red.

## How to rebuild

```bash
cd Code
pip install -r requirements.txt     # also needs LaTeX (texlive) + dvisvgm and ffmpeg
python verify_math.py               # all checks should pass
python build_video.py               # renders all scenes at 1080p → ../GaussianElimination_Video.mp4
python make_docs.py                 # rebuilds Storyboard.pdf and Script_with_timestamps.pdf
```

One scene only (for example after editing `config.py`):

```bash
python build_video.py --scenes S0_Title S7_Summary
```

Preview a scene quickly at low quality: `manim -pql scenes.py S4_Elimination`

### Adding the voice-over

The video ships with a silent audio track. Record your narration reading `Script_with_timestamps.pdf`
(play the video muted alongside), then add it:

```bash
ffmpeg -i GaussianElimination_Video.mp4 -i my_voice.m4a -map 0:v -map 1:a \
       -c:v copy -c:a aac -b:a 192k -shortest GaussianElimination_Video_final.mp4
```

Any video editor (Clipchamp, DaVinci Resolve, iMovie, CapCut) also works: drop the video on one
track and your recording on another. If you speak faster or slower overall, change `WORDS_PER_SEC`
in `Code/timing.py` and re-render so the animation waits for you.

## How the code works (for the viva)

- **`AugMatrix`** (in `scenes.py`) draws an augmented matrix as a grid of separate `MathTex`
  entries plus brackets and the divider bar. `set_entry(i, j, value)` swaps a single entry for a new
  one and returns a `ReplacementTransform`, so a row operation is animated one entry at a time next
  to its arithmetic.
- **`row_op`** in `S4_Elimination` highlights the row and the multiplier entry, writes the operation
  (e.g. `R2 ← R2 − 2R1`), then for each column writes the arithmetic and updates the entry.
- **Timing:** `timing.py` gives each narration cue a slot from its word count (about 150 words per
  minute). `Synced.cue(i)` waits until cue i's start time before playing its animations, and records
  the actual time to `build/cues/`, which `make_docs.py` uses for the timestamped script.
- **3D planes:** each plane is written as z = f(x, y) and drawn with `Surface` over a small square
  around the solution. The axes are shifted so the solution (1, 2, 3) sits at the origin, which keeps
  it centred while the camera rotates. In `S6_Interpretation`, `Transform` morphs plane 2 into
  `y − z = −1` and plane 3 into `z = 3`.
- **2D rotation:** `S3_Intuition` uses a `ValueTracker` t and `always_redraw` to redraw the line
  `(2 − 2t)x + (−1 − 2t)y = −6t` as t goes from 0 to 1.

## References

- G. Strang, *Introduction to Linear Algebra*, 5th ed., Wellesley-Cambridge Press, 2016, Ch. 2.
- D. C. Lay, S. R. Lay, J. J. McDonald, *Linear Algebra and Its Applications*, 6th ed., Pearson, 2021, Ch. 1.
- Manim Community Edition — https://www.manim.community

**Music:** none.
**AI disclosure:** the script, storyboard and animation code were drafted with Claude (Anthropic).
Narration is recorded by the student. All calculations were verified independently (`verify_math.py` and by hand).

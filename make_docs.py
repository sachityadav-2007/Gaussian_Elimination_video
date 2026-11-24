"""Build the two supporting PDFs from the rendered video.

  ../Storyboard.pdf               6-scene storyboard (purpose, visuals, maths, narration, stills)
  ../Script_with_timestamps.pdf   narration to read while recording, with exact start times

Run after build_video.py (it reads build/cues/*.json and grabs stills from the video).
"""
import json
import os
import subprocess
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from config import STUDENT_ID, STUDENT_NAME
from narration import NARRATION, SCENE_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VIDEO = os.path.join(ROOT, "GaussianElimination_Video.mp4")
CUES = os.path.join(HERE, "build", "cues")
STILLS = os.path.join(HERE, "build", "stills")

cues = {s: json.load(open(os.path.join(CUES, s + ".json"))) for s in SCENE_ORDER}
offset, t = {}, 0.0
for s in SCENE_ORDER:
    offset[s] = t
    t += cues[s]["total"]
TOTAL = t


def mmss(x):
    return f"{int(x // 60)}:{x % 60:04.1f}"


def still(scene, k):
    """Frame near the end of cue k of a scene."""
    c = cues[scene]
    ends = c["cues"][1:] + [c["total"]]
    tt = offset[scene] + ends[k] - 0.2
    os.makedirs(STILLS, exist_ok=True)
    out = os.path.join(STILLS, f"{scene}_{k}.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tt:.2f}", "-i", VIDEO, "-frames:v", "1",
                    "-vf", "scale=640:-1", "-q:v", "3", out], check=True)
    return out


ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, spaceAfter=4)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, spaceBefore=6, spaceAfter=4)
B = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=12.5)
SM = ParagraphStyle("sm", parent=B, fontSize=8.5, leading=11)

# --------------------------------------------------------------------------------------
# Storyboard
# --------------------------------------------------------------------------------------
BOARD = [
    ("1. Hook / Context", ["S0_Title", "S1_Hook"], [("S0_Title", 0), ("S1_Hook", 3)],
     "Opening frame (title, concept, name, ID). Pose the puzzle: three equations, every variable in every "
     "equation, so guessing fails. Show the equations as three coloured planes in 3D meeting at one "
     "highlighted point; ask how to find that point systematically.",
     "x+y+z=6, 2x+3y+z=11, x−y+2z=5. Each linear equation in 3 unknowns is a plane; a solution is a "
     "common point of all planes."),
    ("2. Concept Introduction", ["S2_Concept"], [("S2_Concept", 1), ("S2_Concept", 4)],
     "Ax = b with labelled A, x, b; morph into the augmented matrix [A | b] with each row tagged as an "
     "equation. List the three elementary row operations, then a schematic of row echelon form "
     "(pivots, staircase, zeros below). Learning-objective box.",
     "Notation R_i = row i. Swap R_i↔R_j; scale R_i←cR_i (c≠0); replace R_i←R_i+cR_j. Definition "
     "of pivot and row echelon form."),
    ("3. Visual Intuition", ["S3_Intuition"], [("S3_Intuition", 0), ("S3_Intuition", 2)],
     "2D first: lines x+y=3 and 2x−y=0 meet at (1, 2). Apply R2←R2−2R1: the green line rotates "
     "smoothly about (1, 2) until horizontal (y = 2). Show the inverse operation.",
     "(2x−y)−2(x+y)=0−2(3) ⇒ −3y=−6. Every intermediate line (2−2t)x+(−1−2t)y=−6t passes through "
     "(1, 2), so the solution set is unchanged; R2←R2+2R1 undoes the step."),
    ("4. Worked Example", ["S4_Elimination", "S5_BackSub"], [("S4_Elimination", 2), ("S5_BackSub", 3)],
     "Augmented matrix with row labels. Pivot boxed in yellow, target entries in orange, active row in "
     "blue; each entry's arithmetic is written on the right, then the row morphs. Staircase drawn at "
     "the end. Back substitution solves the triangular system bottom-up and checks the answer.",
     "R2←R2−2R1 → [0 1 −1 | −1]; R3←R3−R1 → [0 −2 1 | −1]; R3←R3+2R2 → [0 0 −1 | −3]. "
     "Pivots 1, 1, −1. z=3, y=−1+3=2, x=6−2−3=1. Check: 6 ✓ 11 ✓ 5 ✓."),
    ("5. Interpretation", ["S6_Interpretation"], [("S6_Interpretation", 0), ("S6_Interpretation", 3)],
     "Back to 3D: planes 2 and 3 morph into the eliminated planes (y−z=−1 and the flat plane z=3) "
     "while the yellow point stays fixed. Then three cards: unique / no solution / infinitely many, "
     "each with its echelon pattern and a 2D sketch.",
     "Pivot in every column ⇒ unique solution (1, 2, 3). Row [0 0 0 | 5] means 0=5 ⇒ inconsistent. "
     "A column without a pivot ⇒ free variable ⇒ infinitely many solutions."),
    ("6. Summary & Credits", ["S7_Summary"], [("S7_Summary", 0), ("S7_Summary", 1)],
     "Closing frame: three numbered takeaways, references, tools, music statement, AI disclosure, "
     "student name and ID.",
     "Takeaways: row operations are reversible; pivots drive elimination to echelon form; back "
     "substitution + pivot pattern give the solution and its type."),
]


def storyboard():
    doc = SimpleDocTemplate(os.path.join(ROOT, "Storyboard.pdf"), pagesize=landscape(A4),
                            leftMargin=1.4 * cm, rightMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    el = [Paragraph("Storyboard — Gaussian Elimination: solving a 3 × 3 system", H1),
          Paragraph(f"M3 Animation Video Project · {escape(STUDENT_NAME)} · {escape(STUDENT_ID)} · "
                    f"final length {mmss(TOTAL)} · 1920×1080, 30 fps · made with Manim (Python)", B),
          Spacer(1, 6),
          Paragraph("<b>Learning objective.</b> By the end of this video, the viewer will be able to carry out "
                    "Gaussian elimination on a 3 × 3 system, highlighting pivots and row operations to reach "
                    "row echelon form, and explain why row operations never change the solution set.", B),
          Spacer(1, 4),
          Paragraph("<b>Colour code (same in every scene).</b> Yellow = pivots · Orange = multiplier / row "
                    "operation · Blue = row being changed · Green = new zeros and results · Equation 1/2/3 = "
                    "blue/green/red lines and planes.", B),
          Spacer(1, 8)]
    for i, (name, scenes, shots, visual, maths) in enumerate(BOARD):
        start = offset[scenes[0]]
        end = offset[scenes[-1]] + cues[scenes[-1]]["total"]
        narr = " ".join(" ".join(NARRATION[s]) for s in scenes)
        imgs = [Image(still(s, k), width=8.2 * cm, height=8.2 * cm * 9 / 16) for s, k in shots]
        left = [Paragraph(f"<b>{name}</b>  <font color='#666666'>({mmss(start)} – {mmss(end)})</font>", H2),
                Paragraph("<b>Visual plan.</b> " + escape(visual), B), Spacer(1, 3),
                Paragraph("<b>Mathematics.</b> " + escape(maths), B), Spacer(1, 3),
                Paragraph("<b>Narration.</b> <i>" + escape(narr) + "</i>", SM)]
        t = Table([[left, imgs]], colWidths=[15.8 * cm, 9.0 * cm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                               ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                               ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        el.append(t)
        el.append(PageBreak() if i % 2 == 1 and i < len(BOARD) - 1 else Spacer(1, 10))
    el += [Paragraph("References & credits", H2),
           Paragraph("G. Strang, <i>Introduction to Linear Algebra</i>, 5th ed., Wellesley-Cambridge Press, 2016, Ch. 2. "
                     "D. C. Lay, S. R. Lay, J. J. McDonald, <i>Linear Algebra and Its Applications</i>, 6th ed., Pearson, 2021, Ch. 1. "
                     "Animation: Manim Community Edition (Python). Music: none. "
                     "AI disclosure: script, storyboard and animation code were drafted with Claude (Anthropic); "
                     "narration recorded by the student; all calculations verified independently (Code/verify_math.py and by hand).", B)]
    doc.build(el)


def script():
    doc = SimpleDocTemplate(os.path.join(ROOT, "Script_with_timestamps.pdf"), pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.6 * cm, bottomMargin=1.6 * cm)
    TS = ParagraphStyle("ts", parent=B, fontSize=10.5, leading=15)
    el = [Paragraph("Voice-over script with timestamps", H1),
          Paragraph(f"Video length {mmss(TOTAL)}. Each line starts at the time shown, when its visuals begin. "
                    "Read at a relaxed pace (about 150 words per minute); short pauses after each line are built in. "
                    "Tip: play the video muted while recording so you can follow the animation.", B),
          Spacer(1, 10)]
    names = {"S0_Title": "Opening frame", "S1_Hook": "Scene 1 · Hook", "S2_Concept": "Scene 2 · Concept",
             "S3_Intuition": "Scene 3 · Visual intuition", "S4_Elimination": "Scene 4a · Worked example: elimination",
             "S5_BackSub": "Scene 4b · Worked example: back substitution",
             "S6_Interpretation": "Scene 5 · Interpretation", "S7_Summary": "Scene 6 · Summary & credits"}
    for s in SCENE_ORDER:
        el.append(Paragraph(names[s], H2))
        rows = [[Paragraph(f"<b>{mmss(offset[s] + c)}</b>", TS), Paragraph(escape(txt), TS)]
                for c, txt in zip(cues[s]["cues"], NARRATION[s])]
        t = Table(rows, colWidths=[2.0 * cm, 15.0 * cm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.lightgrey),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        el.append(t)
    doc.build(el)


if __name__ == "__main__":
    storyboard()
    script()
    print("total", mmss(TOTAL))

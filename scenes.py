"""Manim scenes for "Gaussian Elimination: solving a 3x3 system".

Render one scene:   manim -qh scenes.py S4_Elimination
Render everything:  python build_video.py

Example system (used throughout):
    x +  y +  z = 6
   2x + 3y +  z = 11
    x -  y + 2z = 5        solution (x, y, z) = (1, 2, 3)

Colour code (kept the same in every scene):
    YELLOW  pivots              BLUE   row being changed
    ORANGE  multiplier / row op GREEN  new zeros / results
    plane colours: eq.1 BLUE, eq.2 GREEN, eq.3 RED
"""
import json
import os

import numpy as np
from manim import *

from config import STUDENT_ID, STUDENT_NAME
from timing import TIMINGS

HERE = os.path.dirname(os.path.abspath(__file__))
CUE_DIR = os.path.join(HERE, "build", "cues")

BG = "#0f1724"
PIVOT = YELLOW
ACTIVE = BLUE_C
OP = ORANGE
GOOD = GREEN_C
P1, P2, P3 = BLUE_C, GREEN_C, RED_C          # colours of equations 1, 2, 3

config.background_color = BG
SOLUTION = (1, 2, 3)


# --------------------------------------------------------------------------
# Timing: keep visuals in step with the narration script
# --------------------------------------------------------------------------
class Synced:
    """Mixin. Call self.cue(i) right before the visuals for narration segment i."""

    def init_sync(self):
        self.T = TIMINGS[type(self).__name__]
        self.drift = 0.0
        self.cue_times = []

    def cue(self, i):
        target = self.T["segments"][i]["start"] + self.drift
        now = self.renderer.time
        if target - now > 1 / 30:
            self.wait(target - now)
        elif now - target > 0.05:          # previous visuals ran long: push later cues back
            self.drift += now - target
        self.cue_times.append(round(self.renderer.time, 2))

    def pause(self, t):
        if t > 1 / 30:
            self.wait(t)

    def slot(self, i):
        """Length of narration segment i (seconds)."""
        return self.T["segments"][i]["dur"]

    def finish(self):
        target = self.T["total"] + self.drift
        now = self.renderer.time
        if target - now > 1 / 30:
            self.wait(target - now)
        os.makedirs(CUE_DIR, exist_ok=True)
        with open(os.path.join(CUE_DIR, type(self).__name__ + ".json"), "w") as f:
            json.dump({"cues": self.cue_times, "total": round(self.renderer.time, 2)}, f)


def title_bar(text, sub=None):
    t = Text(text, font_size=40, weight=BOLD).to_edge(UP, buff=0.35)
    line = Line(LEFT * 6.6, RIGHT * 6.6, stroke_width=2, color=GREY_B).next_to(t, DOWN, buff=0.18)
    g = VGroup(t, line)
    if sub:
        s = Text(sub, font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.12)
        g.add(s)
    return g


def rows_of(tex, counts):
    """Split a MathTex into rows by glyph counts (for colouring equations)."""
    glyphs = tex[0]
    out, k = [], 0
    for c in counts:
        out.append(VGroup(*glyphs[k:k + c]))
        k += c
    assert k == len(glyphs), (k, len(glyphs))
    return out


SYSTEM_TEX = (r"\begin{array}{rcrcrcr}"
              r"x&+&y&+&z&=&6\\ 2x&+&3y&+&z&=&11\\ x&-&y&+&2z&=&5"
              r"\end{array}")
SYSTEM_COUNTS = [7, 10, 8]


def system_tex(font_size=56):
    m = MathTex(SYSTEM_TEX, font_size=font_size)
    for row, col in zip(rows_of(m, SYSTEM_COUNTS), (P1, P2, P3)):
        row.set_color(col)
    return m


# --------------------------------------------------------------------------
# Augmented matrix whose entries can be changed one row at a time
# --------------------------------------------------------------------------
def fmt(v):
    return str(int(v)) if float(v).is_integer() else str(v)


class AugMatrix(VGroup):
    def __init__(self, rows, center=ORIGIN, cw=1.3, rh=1.0, fs=60, **kw):
        super().__init__(**kw)
        self.cw, self.rh, self.fs, self.c = cw, rh, fs, np.array(center, dtype=float)
        self.vals = [list(r) for r in rows]
        self.cells = [[self.make(i, j, v) for j, v in enumerate(r)] for i, r in enumerate(rows)]
        for r in self.cells:
            self.add(*r)
        top, bot = self.c[1] + rh + 0.5, self.c[1] - rh - 0.5
        xl = self.c[0] + self.x(0) - 0.65
        xr = self.c[0] + self.x(3) + 0.65
        xb = self.c[0] + (self.x(2) + self.x(3)) / 2
        k = 0.22
        self.lb = VMobject().set_points_as_corners([[xl + k, top, 0], [xl, top, 0], [xl, bot, 0], [xl + k, bot, 0]])
        self.rb = VMobject().set_points_as_corners([[xr - k, top, 0], [xr, top, 0], [xr, bot, 0], [xr - k, bot, 0]])
        self.bar = Line([xb, top - 0.15, 0], [xb, bot + 0.15, 0])
        for m in (self.lb, self.rb, self.bar):
            m.set_stroke(WHITE, 3)
        self.add(self.lb, self.rb, self.bar)

    def x(self, j):
        return (j - 1.5) * self.cw + (0.4 if j == 3 else 0)

    def pos(self, i, j):
        return self.c + np.array([self.x(j), (1 - i) * self.rh, 0])

    def make(self, i, j, v, color=WHITE):
        return MathTex(fmt(v), font_size=self.fs, color=color).move_to(self.pos(i, j))

    def row(self, i):
        return VGroup(*self.cells[i])

    def col(self, j, rows=(0, 1, 2)):
        return VGroup(*[self.cells[i][j] for i in rows])

    def box(self, i, j, color=PIVOT, buff=0.14):
        return SurroundingRectangle(self.cells[i][j], color=color, buff=buff, stroke_width=4)

    def set_entry(self, i, j, v, color=WHITE):
        new = self.make(i, j, v, color)
        old = self.cells[i][j]
        self.remove(old)
        self.add(new)
        self.cells[i][j] = new
        self.vals[i][j] = v
        return ReplacementTransform(old, new)


# --------------------------------------------------------------------------
# 3D helpers
# --------------------------------------------------------------------------
def make_axes3d():
    ax = ThreeDAxes(x_range=[-1, 3, 1], y_range=[0, 4, 1], z_range=[-1, 7, 1],
                    x_length=4.0, y_length=4.0, z_length=4.8,
                    axis_config={"include_ticks": True, "stroke_width": 2})
    return ax.shift(-ax.c2p(*SOLUTION))      # solution point sits at the origin


def plane(axes, f, color, opacity=0.55):
    s = Surface(lambda u, v: axes.c2p(u, v, f(u, v)),
                u_range=[0.15, 1.85], v_range=[1.15, 2.85], resolution=(8, 8),
                fill_opacity=opacity, checkerboard_colors=[color, color],
                stroke_color=color, stroke_width=0.6, stroke_opacity=0.8)
    return s


F1 = lambda x, y: 6 - x - y                 # x + y + z = 6
F2 = lambda x, y: 11 - 2 * x - 3 * y        # 2x + 3y + z = 11
F3 = lambda x, y: (5 - x + y) / 2           # x - y + 2z = 5
G2 = lambda x, y: y + 1                     # y - z = -1     (after R2 <- R2 - 2R1)
G3 = lambda x, y: 3 + 0 * x                 # -z = -3        (after elimination)


def axis_labels(axes):
    return VGroup(
        MathTex("x", font_size=44).move_to(axes.c2p(3.5, 0, 0)),
        MathTex("y", font_size=44).move_to(axes.c2p(0, 4.5, 0)),
        MathTex("z", font_size=44).move_to(axes.c2p(0, 0, 7.5)),
    )


def legend(lines, colors, font_size=40):
    rows = VGroup()
    for tex, col in zip(lines, colors):
        sw = Square(0.32, fill_color=col, fill_opacity=0.85, stroke_width=0)
        rows.add(VGroup(sw, MathTex(tex, font_size=font_size, color=col)).arrange(RIGHT, buff=0.25))
    return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)


# ==========================================================================
# Scene 0 - Opening frame
# ==========================================================================
class S0_Title(Synced, Scene):
    def construct(self):
        self.init_sync()
        self.cue(0)
        title = Text("Gaussian Elimination", font_size=80, weight=BOLD)
        sub = Text("How row operations solve a 3 × 3 linear system",
                   font_size=36, color=GREY_A)
        course = Text("M3 · Linear Algebra and Calculus · Animation Video Project",
                      font_size=26, color=GREY_B)
        who = Text(f"{STUDENT_NAME}   |   {STUDENT_ID}", font_size=32, color=PIVOT)
        top = VGroup(title, sub).arrange(DOWN, buff=0.35).shift(UP * 1.9)
        mat = AugMatrix([[1, 1, 1, 6], [2, 3, 1, 11], [1, -1, 2, 5]], center=DOWN * 0.75, fs=40, cw=0.9, rh=0.62)
        bottom = VGroup(course, who).arrange(DOWN, buff=0.25).to_edge(DOWN, buff=0.55)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(sub, shift=UP * 0.2), FadeIn(mat), run_time=1.0)
        self.play(FadeIn(bottom), run_time=0.8)
        # the decorative matrix collapses to echelon form (zeros below the diagonal)
        ech = [[1, 1, 1, 6], [0, 1, -1, -1], [0, 0, -1, -3]]     # its row echelon form
        anims = []
        for i in (1, 2):
            for j in range(4):
                col = GOOD if j < i else (PIVOT if j == i else WHITE)
                anims.append(mat.set_entry(i, j, ech[i][j], col))
        self.play(*anims, mat.cells[0][0].animate.set_color(PIVOT), run_time=1.5)
        self.finish()


# ==========================================================================
# Scene 1 - Hook: three equations = three planes
# ==========================================================================
class S1_Hook(Synced, ThreeDScene):
    def construct(self):
        self.init_sync()
        # --- cue 0: the system
        self.cue(0)
        sys_ = system_tex(64)
        self.add_fixed_in_frame_mobjects(sys_)
        sys_.move_to(ORIGIN)
        rows = rows_of(sys_, SYSTEM_COUNTS)
        for r in rows:
            self.play(Write(r), run_time=1.4)
        # --- cue 1: every equation contains every variable
        self.cue(1)
        q = MathTex(r"x = \,?\quad y = \,?\quad z = \,?", font_size=56, color=GREY_A)
        self.add_fixed_in_frame_mobjects(q)
        q.next_to(sys_, DOWN, buff=0.7)
        self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
        rects = VGroup(*[SurroundingRectangle(r, color=OP, buff=0.1) for r in rows])
        self.add_fixed_in_frame_mobjects(rects)
        self.play(LaggedStart(*[Create(r) for r in rects], lag_ratio=0.3), run_time=1.5)
        self.play(FadeOut(rects), FadeOut(q), run_time=0.6)
        # --- cue 2: planes
        self.cue(2)
        self.play(sys_.animate.scale(0.55).to_corner(UL, buff=0.4), run_time=1.0)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-40 * DEGREES, zoom=0.85)
        axes = make_axes3d()
        labels = axis_labels(axes)
        self.add_fixed_orientation_mobjects(*labels)
        p1, p2, p3 = plane(axes, F1, P1), plane(axes, F2, P2), plane(axes, F3, P3)
        self.play(Create(axes), FadeIn(labels), run_time=1.0)
        for p in (p1, p2, p3):
            self.play(FadeIn(p), run_time=0.9)
        pt = Sphere(radius=0.09, color=PIVOT).move_to(axes.c2p(*SOLUTION))
        pt.set_color(PIVOT)
        self.play(FadeIn(pt, scale=3), run_time=0.6)
        self.begin_ambient_camera_rotation(rate=0.12)
        # --- cue 3: the question
        self.cue(3)
        ques = Text("Where do all three planes meet?", font_size=36, color=PIVOT)
        self.add_fixed_in_frame_mobjects(ques)
        ques.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(ques, shift=UP * 0.2), run_time=0.8)
        self.pause((self.slot(3) - 3.2))
        ans = Text("→  Gaussian elimination", font_size=40, weight=BOLD, color=GOOD)
        self.add_fixed_in_frame_mobjects(ans)
        ans.to_edge(DOWN, buff=0.5)
        self.play(ReplacementTransform(ques, ans), run_time=0.8)
        self.finish()
        self.stop_ambient_camera_rotation()


# ==========================================================================
# Scene 2 - Concept introduction: Ax = b, augmented matrix, row ops, echelon form
# ==========================================================================
class S2_Concept(Synced, Scene):
    def construct(self):
        self.init_sync()
        head = title_bar("Notation and the tools")
        self.add(head)
        # --- cue 0: Ax = b
        self.cue(0)
        A = Matrix([[1, 1, 1], [2, 3, 1], [1, -1, 2]], h_buff=0.9)
        xv = Matrix([["x"], ["y"], ["z"]])
        bv = Matrix([[6], [11], [5]])
        eq = MathTex("=")
        axb = VGroup(A, xv, eq, bv).arrange(RIGHT, buff=0.75).shift(UP * 0.2)
        A.set_color(WHITE)
        bv.get_entries().set_color(OP)
        labs = VGroup(
            Text("A: coefficients", font_size=26).next_to(A, DOWN, buff=0.35),
            Text("x: unknowns", font_size=26).next_to(xv, DOWN, buff=0.35),
            Text("b: constants", font_size=26, color=OP).next_to(bv, DOWN, buff=0.35),
        )
        big = MathTex("A\\mathbf{x} = \\mathbf{b}", font_size=60).next_to(axb, UP, buff=0.5)
        self.play(Write(big), run_time=0.8)
        self.play(FadeIn(axb), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.15) for l in labs], lag_ratio=0.4), run_time=1.6)
        # --- cue 1: augmented matrix
        self.cue(1)
        aug = AugMatrix([[1, 1, 1, 6], [2, 3, 1, 11], [1, -1, 2, 5]], center=DOWN * 0.2 + LEFT * 1.0, fs=54)
        aug.col(3).set_color(OP)
        auglab = MathTex(r"[\,A \mid \mathbf{b}\,]", font_size=56).next_to(aug, UP, buff=0.4)
        self.play(FadeOut(labs), FadeOut(big), ReplacementTransform(axb, aug), run_time=1.4)
        self.play(Write(auglab), run_time=0.6)
        tags = VGroup(*[MathTex(r"\leftarrow\ \text{equation } %d" % (i + 1), font_size=36,
                                color=c).next_to(aug.rb, RIGHT, buff=0.4).set_y(aug.pos(i, 0)[1])
                        for i, c in enumerate((P1, P2, P3))])
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.2) for t in tags], lag_ratio=0.3), run_time=1.2)
        # --- cue 2: three row operations
        self.cue(2)
        self.play(FadeOut(VGroup(aug, auglab, tags)), run_time=0.6)
        ops_t = Text("Elementary row operations", font_size=32, weight=BOLD).move_to([-6.6, 2.2, 0], aligned_edge=LEFT)
        ops = VGroup(
            VGroup(Text("1. Swap", font_size=30), MathTex(r"R_i \leftrightarrow R_j", font_size=44, color=OP)),
            VGroup(Text("2. Scale", font_size=30), MathTex(r"R_i \leftarrow c\,R_i \;\;(c \neq 0)", font_size=44, color=OP)),
            VGroup(Text("3. Replace", font_size=30), MathTex(r"R_i \leftarrow R_i + c\,R_j", font_size=44, color=OP)),
        )
        for o in ops:
            o.arrange(RIGHT, buff=0.4)
        ops.arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(ops_t, DOWN, buff=0.5).align_to(ops_t, LEFT)
        rdef = MathTex(r"R_i = \text{row } i", font_size=32, color=GREY_B).next_to(ops, DOWN, buff=0.45).align_to(ops, LEFT)
        self.play(FadeIn(ops_t), run_time=0.5)
        per = max(0.8, (self.slot(2) - 1.8) / 3)
        for o in ops:
            self.play(FadeIn(o, shift=RIGHT * 0.2), run_time=0.7)
            self.pause((per - 0.7))
        self.play(FadeIn(rdef), run_time=0.5)
        # --- cue 3: row echelon form
        self.cue(3)
        ef_t = Text("Goal: row echelon form", font_size=32, weight=BOLD).move_to([3.9, 2.2, 0])
        sym = [[r"\blacksquare", "*", "*", "*"], ["0", r"\blacksquare", "*", "*"], ["0", "0", r"\blacksquare", "*"]]
        ef = VGroup()
        cells = {}
        for i in range(3):
            for j in range(4):
                m = MathTex(sym[i][j], font_size=50).move_to([2.2 + j * 0.95 + (0.3 if j == 3 else 0), 0.9 - i * 0.85, 0])
                if i == j:
                    m.set_color(PIVOT)
                elif j < i:
                    m.set_color(GOOD)
                cells[i, j] = m
                ef.add(m)
        barx = 2.2 + 2.5 * 0.95 + 0.15
        ef.add(Line([barx, 1.4, 0], [barx, -1.4, 0], stroke_width=3))
        stair = VMobject(stroke_color=PIVOT, stroke_width=3).set_points_as_corners([
            [1.75, 0.45, 0], [2.65, 0.45, 0], [2.65, -0.4, 0], [3.6, -0.4, 0], [3.6, -1.25, 0], [4.55, -1.25, 0]])
        pv = Text("pivot", font_size=28, color=PIVOT).move_to([0.6, 0.9, 0])
        pv_arrow = Arrow(pv.get_right(), cells[0, 0].get_left(), buff=0.15, color=PIVOT, stroke_width=3)
        zl = Text("zeros below pivots", font_size=28, color=GOOD).move_to([3.0, -2.2, 0])
        self.play(FadeIn(ef_t), run_time=0.5)
        self.play(FadeIn(ef), run_time=1.0)
        self.play(Create(stair), FadeIn(pv), GrowArrow(pv_arrow), run_time=1.2)
        self.play(FadeIn(zl), *[Indicate(cells[i, j], color=GOOD) for (i, j) in [(1, 0), (2, 0), (2, 1)]], run_time=1.2)
        # --- cue 4: learning objective
        self.cue(4)
        box_txt = Paragraph(
            "Learning objective: by the end of this video you will be able to carry out",
            "Gaussian elimination on a 3 × 3 system and explain why row operations",
            "never change its solution set.", font_size=26, alignment="center", line_spacing=0.8)
        box = SurroundingRectangle(box_txt, color=GOOD, buff=0.25, corner_radius=0.1)
        obj = VGroup(box, box_txt).to_edge(DOWN, buff=0.35)
        self.play(FadeOut(zl), Create(box), Write(box_txt), run_time=2.0)
        self.finish()


# ==========================================================================
# Scene 3 - Visual intuition in 2D: replacement keeps the intersection
# ==========================================================================
class S3_Intuition(Synced, Scene):
    def construct(self):
        self.init_sync()
        head = title_bar("Why row operations are allowed", "Intuition in 2D first")
        self.add(head)
        ax = Axes(x_range=[-1, 4, 1], y_range=[-1, 4, 1], x_length=5.6, y_length=5.6,
                  axis_config={"include_numbers": True, "font_size": 26}).to_edge(LEFT, buff=0.7).shift(DOWN * 0.55)
        grid = NumberPlane(x_range=[-1, 4, 1], y_range=[-1, 4, 1], x_length=5.6, y_length=5.6,
                           background_line_style={"stroke_opacity": 0.25}).move_to(ax.c2p(1.5, 1.5))
        xl = MathTex("x", font_size=34).next_to(ax.x_axis.get_end(), RIGHT, buff=0.1)
        yl = MathTex("y", font_size=34).next_to(ax.y_axis.get_end(), UP, buff=0.1)
        t = ValueTracker(0)

        def l1():
            return ax.plot(lambda x: 3 - x, x_range=[-1, 4], color=P1, stroke_width=5)

        def l2_of(tv):
            # (2-2t)x + (-1-2t)y = -6t   ->   y = ((2-2t)x + 6t) / (1+2t)
            return ax.plot(lambda x: ((2 - 2 * tv) * x + 6 * tv) / (1 + 2 * tv),
                           x_range=[-0.5, 2.0] if tv < 0.05 else [-1, 4], color=P2, stroke_width=5)

        line1 = l1()
        line2 = always_redraw(lambda: l2_of(t.get_value()))
        dot = Dot(ax.c2p(1, 2), color=PIVOT, radius=0.11)
        dl = MathTex("(1,\\,2)", font_size=36, color=PIVOT).next_to(dot, UR, buff=0.08)

        e1 = MathTex(r"R_1:\; x + y = 3", font_size=46, color=P1)
        e2 = MathTex(r"R_2:\; 2x - y = 0", font_size=46, color=P2)
        eqs = VGroup(e1, e2).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0.6, 1.55, 0], aligned_edge=LEFT)
        # --- cue 0
        self.cue(0)
        self.play(Create(grid), Create(ax), FadeIn(xl, yl), run_time=1.2)
        self.play(Write(e1), Create(line1), run_time=1.4)
        self.play(Write(e2), Create(line2), run_time=1.4)
        self.play(FadeIn(dot, scale=2), Write(dl), run_time=0.8)
        # --- cue 1: the row operation, written out
        self.cue(1)
        op = MathTex(r"R_2 \leftarrow R_2 - 2R_1", font_size=46, color=OP).next_to(eqs, DOWN, buff=0.45).align_to(eqs, LEFT)
        c1 = MathTex(r"(2x - y) - 2(x + y) = 0 - 2(3)", font_size=38).next_to(op, DOWN, buff=0.35).align_to(eqs, LEFT)
        c2 = MathTex(r"-3y = -6", font_size=46, color=P2).next_to(c1, DOWN, buff=0.3).align_to(eqs, LEFT)
        self.play(Write(op), run_time=0.9)
        self.play(Write(c1), run_time=1.4)
        self.play(Write(c2), run_time=0.9)
        # --- cue 2: line 2 rotates about (1, 2)
        self.cue(2)
        self.play(t.animate.set_value(1), run_time=4.0, rate_func=smooth)
        self.play(Flash(dot, color=PIVOT, line_length=0.3), run_time=0.8)
        e2n = MathTex(r"R_2:\; -3y = -6", font_size=46, color=P2).move_to(e2, aligned_edge=LEFT)
        self.play(TransformMatchingShapes(e2, e2n), run_time=1.0)
        undo = MathTex(r"\text{undo: } R_2 \leftarrow R_2 + 2R_1", font_size=36, color=GREY_A).next_to(c2, DOWN, buff=0.35).align_to(eqs, LEFT)
        self.play(FadeIn(undo, shift=UP * 0.15), run_time=0.7)
        # --- cue 3: the take-away
        self.cue(3)
        msg = Text("Simpler picture,\nsame intersection point.", font_size=30, color=GOOD, line_spacing=0.9)
        msg2 = Text("Swap, scale, replace are all reversible\n⇒ the solution set is preserved",
                    font_size=24, color=GREY_A, line_spacing=0.9)
        side = VGroup(msg, msg2).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(op, DOWN, buff=0.5).align_to(eqs, LEFT)
        self.play(FadeOut(VGroup(c1, c2, undo)), run_time=0.5)
        self.play(FadeIn(msg, shift=UP * 0.15), run_time=0.8)
        self.pause((self.slot(3) * 0.45 - 1.3))
        self.play(FadeIn(msg2, shift=UP * 0.15), run_time=0.8)
        self.finish()


# ==========================================================================
# Scene 4 - Worked example: forward elimination on the 3x3 system
# ==========================================================================
class S4_Elimination(Synced, Scene):
    def construct(self):
        self.init_sync()
        head = title_bar("Worked example: forward elimination")
        self.add(head)
        M = AugMatrix([[1, 1, 1, 6], [2, 3, 1, 11], [1, -1, 2, 5]], center=[-3.5, -0.35, 0])
        rlabels = VGroup(*[MathTex(f"R_{i+1}", font_size=40, color=GREY_B).next_to(M.lb, LEFT, buff=0.35).set_y(M.pos(i, 0)[1])
                           for i in range(3)])
        panel_x = 0.6
        step = Text("", font_size=32)

        def step_label(s):
            return Text(s, font_size=32, weight=BOLD, color=PIVOT).move_to([panel_x, 2.2, 0], aligned_edge=LEFT)

        def calc_lines(lines, top):
            g = VGroup(*[MathTex(l, font_size=42) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
            g.next_to(top, DOWN, buff=0.4).align_to(top, LEFT)
            return g

        def row_op(i, new_vals, op_tex, lines, slot_len, mult_entry):
            """Highlight row i, show the operation & arithmetic, then rewrite the row."""
            op = MathTex(op_tex, font_size=50, color=OP).move_to([panel_x, 1.35, 0], aligned_edge=LEFT)
            hl = SurroundingRectangle(M.row(i), color=ACTIVE, buff=0.12, stroke_width=4)
            self.play(Create(hl), Indicate(M.cells[i][mult_entry], color=OP, scale_factor=1.3), run_time=0.9)
            self.play(Write(op), run_time=0.8)
            calc = calc_lines(lines, op)
            each = max(0.55, (slot_len - 4.2) / 4)
            for j, l in enumerate(calc):
                self.play(Write(l), run_time=min(0.9, each))
                col = GOOD if new_vals[j] == 0 and j < 3 else WHITE
                self.play(M.set_entry(i, j, new_vals[j], col), run_time=0.45)
                self.pause((each - 0.9 - 0.45))
            self.play(FadeOut(hl), run_time=0.4)
            return VGroup(op, calc)

        # --- cue 0
        self.cue(0)
        self.play(FadeIn(M), FadeIn(rlabels), run_time=1.3)
        # --- cue 1: pivot 1
        self.cue(1)
        s1 = step_label("Step 1 · pivot in column 1")
        piv1 = M.box(0, 0)
        below1 = SurroundingRectangle(M.col(0, (1, 2)), color=OP, buff=0.15, stroke_width=3)
        self.play(FadeIn(s1), Create(piv1), M.cells[0][0].animate.set_color(PIVOT), run_time=1.0)
        self.play(Create(below1), run_time=0.8)
        tgt = Text("make these 0", font_size=28, color=OP).next_to(below1, DOWN, buff=0.15)
        self.play(FadeIn(tgt), run_time=0.5)
        # --- cue 2: R2 <- R2 - 2R1
        self.cue(2)
        self.play(FadeOut(below1), FadeOut(tgt), run_time=0.4)
        g = row_op(1, [0, 1, -1, -1], r"R_2 \leftarrow R_2 - 2R_1",
                   [r"2 - 2(1) = 0", r"3 - 2(1) = 1", r"1 - 2(1) = -1", r"11 - 2(6) = -1"],
                   self.slot(2), 0)
        # --- cue 3: R3 <- R3 - R1
        self.cue(3)
        self.play(FadeOut(g), run_time=0.4)
        g = row_op(2, [0, -2, 1, -1], r"R_3 \leftarrow R_3 - 1\cdot R_1",
                   [r"1 - 1 = 0", r"-1 - 1 = -2", r"2 - 1 = 1", r"5 - 6 = -1"],
                   self.slot(3), 0)
        # --- cue 4: pivot 2
        self.cue(4)
        s2 = step_label("Step 2 · pivot in column 2")
        piv2 = M.box(1, 1)
        self.play(FadeOut(g), ReplacementTransform(s1, s2), run_time=0.6)
        self.play(ReplacementTransform(piv1, piv2), M.cells[1][1].animate.set_color(PIVOT), run_time=1.0)
        below2 = SurroundingRectangle(M.cells[2][1], color=OP, buff=0.15, stroke_width=3)
        self.play(Create(below2), run_time=0.6)
        # --- cue 5: R3 <- R3 + 2R2
        self.cue(5)
        self.play(FadeOut(below2), run_time=0.3)
        g = row_op(2, [0, 0, -1, -3], r"R_3 \leftarrow R_3 + 2R_2",
                   [r"0 + 2(0) = 0", r"-2 + 2(1) = 0", r"1 + 2(-1) = -1", r"-1 + 2(-1) = -3"],
                   self.slot(5), 1)
        # --- cue 6: echelon form
        self.cue(6)
        self.play(FadeOut(g), FadeOut(piv2), run_time=0.5)
        self.play(M.cells[2][2].animate.set_color(PIVOT), run_time=0.4)
        boxes = VGroup(*[M.box(k, k) for k in range(3)])
        c = M.c
        cw, rh = M.cw, M.rh
        xs = [c[0] + M.x(j) - cw / 2 for j in range(4)]
        ys = [c[1] + (1 - i) * rh - rh / 2 for i in range(3)]
        stair = VMobject(stroke_color=PIVOT, stroke_width=4).set_points_as_corners([
            [xs[0], ys[0], 0], [xs[1], ys[0], 0], [xs[1], ys[1], 0], [xs[2], ys[1], 0],
            [xs[2], ys[2], 0], [xs[3] - 0.05, ys[2], 0]])
        done = Text("Row echelon form ✓", font_size=40, weight=BOLD, color=GOOD).move_to([panel_x, 1.2, 0], aligned_edge=LEFT)
        pivs = MathTex(r"\text{pivots: } 1,\ 1,\ -1", font_size=44, color=PIVOT).next_to(done, DOWN, buff=0.45).align_to(done, LEFT)
        zeros = MathTex(r"\text{zeros below every pivot}", font_size=40, color=GOOD).next_to(pivs, DOWN, buff=0.35).align_to(done, LEFT)
        self.play(FadeOut(s2), Create(boxes), Create(stair), run_time=1.2)
        self.play(Write(done), run_time=0.8)
        self.play(FadeIn(pivs), run_time=0.6)
        self.play(FadeIn(zeros), *[Indicate(M.cells[i][j], color=GOOD) for i, j in [(1, 0), (2, 0), (2, 1)]], run_time=1.0)
        self.finish()


# ==========================================================================
# Scene 5 - Back substitution and check
# ==========================================================================
class S5_BackSub(Synced, Scene):
    def construct(self):
        self.init_sync()
        head = title_bar("Back substitution")
        self.add(head)
        cap = Text("Echelon form, written as equations:", font_size=28, color=GREY_A).move_to([-6.4, 2.25, 0], aligned_edge=LEFT)
        tri = MathTex(r"\begin{array}{rcrcrcr} x&+&y&+&z&=&6\\ &&y&-&z&=&-1\\ &&&&-z&=&-3\end{array}",
                      font_size=48)
        tri.next_to(cap, DOWN, buff=0.35).align_to(cap, LEFT)
        M = cap
        arrow = VGroup()
        r1, r2, r3 = rows_of(tri, [7, 6, 5])
        res_x = tri.get_right()[0] + 0.9
        # --- cue 0
        self.cue(0)
        self.play(FadeIn(M), run_time=0.7)
        self.play(Write(arrow), Write(tri), run_time=1.6)
        b3 = SurroundingRectangle(r3, color=ACTIVE, buff=0.1)
        self.play(Create(b3), run_time=0.6)
        z_ = MathTex(r"\Rightarrow\; z = 3", font_size=44, color=GOOD).move_to([res_x, r3.get_y(), 0], aligned_edge=LEFT)
        self.play(Write(z_), run_time=0.9)
        # --- cue 1
        self.cue(1)
        b2 = SurroundingRectangle(r2, color=ACTIVE, buff=0.1)
        self.play(ReplacementTransform(b3, b2), run_time=0.6)
        y_ = MathTex(r"y - 3 = -1 \;\Rightarrow\; y = 2", font_size=44).move_to(z_, aligned_edge=LEFT).set_y(r2.get_y())
        y_[0][-3:].set_color(GOOD)
        self.play(Write(y_), run_time=1.4)
        # --- cue 2
        self.cue(2)
        b1 = SurroundingRectangle(r1, color=ACTIVE, buff=0.1)
        self.play(ReplacementTransform(b2, b1), run_time=0.6)
        x_ = MathTex(r"x + 2 + 3 = 6 \;\Rightarrow\; x = 1", font_size=44).move_to(z_, aligned_edge=LEFT).set_y(r1.get_y())
        x_[0][-3:].set_color(GOOD)
        self.play(Write(x_), run_time=1.4)
        self.play(FadeOut(b1), run_time=0.4)
        # --- cue 3: check
        self.cue(3)
        chk_t = Text("Check in the original equations", font_size=32, weight=BOLD).move_to([0, -0.9, 0])
        checks = VGroup(
            MathTex(r"1 + 2 + 3 = 6", r"\ \checkmark", font_size=44, color=P1),
            MathTex(r"2(1) + 3(2) + 3 = 11", r"\ \checkmark", font_size=44, color=P2),
            MathTex(r"1 - 2 + 2(3) = 5", r"\ \checkmark", font_size=44, color=P3),
        ).arrange(RIGHT, buff=0.7).next_to(chk_t, DOWN, buff=0.45)
        for c in checks:
            c[1].set_color(GOOD)
        self.play(FadeIn(chk_t), run_time=0.5)
        for c in checks:
            self.play(Write(c), run_time=0.9)
        sol = MathTex(r"(x,\,y,\,z) = (1,\,2,\,3)", font_size=60, color=PIVOT)
        sbox = SurroundingRectangle(sol, color=PIVOT, buff=0.22)
        VGroup(sol, sbox).to_edge(DOWN, buff=0.5)
        self.play(Write(sol), Create(sbox), run_time=1.0)
        self.finish()


# ==========================================================================
# Scene 6 - Interpretation: what the planes did, and the other cases
# ==========================================================================
class S6_Interpretation(Synced, ThreeDScene):
    def construct(self):
        self.init_sync()
        head = title_bar("Interpretation")
        self.add_fixed_in_frame_mobjects(head)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-40 * DEGREES, zoom=0.9)
        axes = make_axes3d()
        labels = axis_labels(axes)
        self.add_fixed_orientation_mobjects(*labels)
        p1, p2, p3 = plane(axes, F1, P1), plane(axes, F2, P2), plane(axes, F3, P3)
        pt = Sphere(radius=0.09).move_to(axes.c2p(*SOLUTION)).set_color(PIVOT)
        leg = legend([r"x+y+z=6", r"2x+3y+z=11", r"x-y+2z=5"], [P1, P2, P3])
        self.add_fixed_in_frame_mobjects(leg)
        leg.scale(0.85).to_corner(UL, buff=0.5).shift(DOWN * 0.9)
        # --- cue 0: planes morph to the eliminated system
        self.cue(0)
        self.play(Create(axes), FadeIn(labels), FadeIn(p1), FadeIn(p2), FadeIn(p3), FadeIn(pt), run_time=1.5)
        self.begin_ambient_camera_rotation(rate=0.1)
        new2 = MathTex(r"y - z = -1", font_size=40, color=P2).move_to(leg[1][1], aligned_edge=LEFT)
        new3 = MathTex(r"-z = -3", font_size=40, color=P3).move_to(leg[2][1], aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(new2, new3)
        self.remove(new2, new3)
        self.play(Transform(p2, plane(axes, G2, P2)), Transform(leg[1][1], new2), run_time=2.5)
        self.play(Transform(p3, plane(axes, G3, P3)), Transform(leg[2][1], new3), run_time=2.5)
        note = Text("same point on every plane", font_size=28, color=GREY_A)
        self.add_fixed_in_frame_mobjects(note)
        note.next_to(leg, DOWN, buff=0.45).align_to(leg, LEFT)
        self.play(FadeIn(note), run_time=0.6)
        # --- cue 1: unique solution
        self.cue(1)
        uniq = VGroup(MathTex(r"\text{3 pivots}\;\Rightarrow\;\text{one point}", font_size=40, color=PIVOT),
                      MathTex(r"(1,\,2,\,3)", font_size=48, color=PIVOT)).arrange(DOWN, buff=0.25)
        self.add_fixed_in_frame_mobjects(uniq)
        uniq.next_to(note, DOWN, buff=0.6).align_to(leg, LEFT)
        self.play(FadeIn(uniq, shift=UP * 0.2), pt.animate.scale(1.8), run_time=1.0)
        self.play(pt.animate.scale(1 / 1.8), run_time=0.6)
        # --- cue 2: no-solution case (switch to 2D cards)
        self.cue(2)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in (axes, labels, p1, p2, p3, pt, leg, note, uniq)], run_time=0.8)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1.0)

        def card(title, mat_rows, verdict, col, sketch):
            t = Text(title, font_size=28, weight=BOLD, color=col)
            m = MathTex(mat_rows, font_size=36)
            v = Text(verdict, font_size=26, color=col)
            g = VGroup(t, m, sketch, v).arrange(DOWN, buff=0.35)
            box = SurroundingRectangle(g, color=col, buff=0.3, corner_radius=0.12)
            return VGroup(box, g)

        def sk(lines_fn):
            fr = Square(1.6, stroke_color=GREY_B, stroke_width=1.5)
            return VGroup(fr, *lines_fn(fr))

        uniq_s = sk(lambda f: [Line(f.get_corner(DL), f.get_corner(UR), color=P1),
                               Line(f.get_corner(UL), f.get_corner(DR), color=P2),
                               Dot(f.get_center(), color=PIVOT)])
        none_s = sk(lambda f: [Line(f.get_corner(DL) + UP * 0.3, f.get_corner(UR) + DOWN * 0.5 + LEFT * 0.0, color=P1),
                               Line(f.get_corner(DL) + UP * 0.8 + RIGHT * 0.0, f.get_corner(UR) + DOWN * 0.0, color=P2)])
        inf_s = sk(lambda f: [Line(f.get_corner(DL), f.get_corner(UR), color=P1, stroke_width=8),
                              DashedLine(f.get_corner(DL), f.get_corner(UR), color=P2, stroke_width=4)])
        c1 = card("pivot in every column", r"\left[\begin{array}{ccc|c}1&1&1&6\\0&1&-1&-1\\0&0&-1&-3\end{array}\right]",
                  "unique solution", PIVOT, uniq_s)
        c2 = card("row [0 0 0 | 5]", r"\left[\begin{array}{ccc|c}1&1&1&6\\0&1&-1&-1\\0&0&0&5\end{array}\right]",
                  "0 = 5 → no solution", RED_C, none_s)
        c3 = card("column without a pivot", r"\left[\begin{array}{ccc|c}1&1&1&6\\0&1&-1&-1\\0&0&0&0\end{array}\right]",
                  "free variable → infinitely many", BLUE_C, inf_s)
        cards = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.45).scale_to_fit_width(13.2).next_to(head, DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(cards)
        self.remove(cards)
        self.play(FadeIn(c1, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(c2, shift=UP * 0.2), run_time=0.9)
        z = c2[1][1]
        self.play(Indicate(z, color=RED_C), run_time=1.0)
        # --- cue 3: infinitely many
        self.cue(3)
        self.play(FadeIn(c3, shift=UP * 0.2), run_time=0.9)
        self.finish()


# ==========================================================================
# Scene 7 - Summary & credits (closing frame)
# ==========================================================================
class S7_Summary(Synced, Scene):
    def construct(self):
        self.init_sync()
        head = title_bar("Summary")
        self.add(head)
        items = [
            ("1", "Row operations are reversible, so they never change the solution set."),
            ("2", "Pivots guide elimination: clear the entries below each pivot → echelon form."),
            ("3", "Back substitution reads off the solution; the pivots tell us if it is unique."),
        ]
        rows = VGroup()
        for n, s in items:
            badge = VGroup(Circle(0.28, color=PIVOT, fill_opacity=0.2), Text(n, font_size=28, color=PIVOT))
            rows.add(VGroup(badge, Text(s, font_size=27)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32).next_to(head, DOWN, buff=0.4)
        if rows.width > 13.0:
            rows.scale_to_fit_width(13.0)
        rows.set_x(0)
        # --- cue 0
        self.cue(0)
        per = (self.slot(0) - 0.8) / 3
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
            self.pause((per - 0.8))
        # --- cue 1: credits
        self.cue(1)
        sep = Line(LEFT * 6.6, RIGHT * 6.6, stroke_width=1.5, color=GREY_B).next_to(rows, DOWN, buff=0.45)
        cred = VGroup(
            Text("References", font_size=26, weight=BOLD, color=GREY_A),
            Text("G. Strang, Introduction to Linear Algebra, 5th ed., Wellesley-Cambridge Press, 2016 (Ch. 2).", font_size=20),
            Text("D. C. Lay, S. R. Lay, J. J. McDonald, Linear Algebra and Its Applications, 6th ed., Pearson, 2021 (Ch. 1).", font_size=20),
            Text("Tools: Manim Community Edition (Python) for all animation.   Music: none.", font_size=20),
            Text("AI disclosure: script, storyboard and animation code drafted with Claude (Anthropic);", font_size=20, color=OP),
            Text("narration recorded by the student; all calculations checked independently.", font_size=20, color=OP),
            Text(f"{STUDENT_NAME}   |   {STUDENT_ID}", font_size=26, color=PIVOT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).next_to(sep, DOWN, buff=0.3).align_to(rows, LEFT)
        cred[-1].shift(DOWN * 0.12)
        if cred.width > 13.0:
            cred.scale_to_fit_width(13.0).align_to(rows, LEFT)
        self.play(Create(sep), FadeIn(cred, shift=UP * 0.2), run_time=1.2)
        self.finish()

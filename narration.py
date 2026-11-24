"""Voice-over script for the Gaussian elimination video.

Each scene is a list of narration segments ("cues"). The animation code in
scenes.py starts the visuals for segment i exactly when segment i begins to be
spoken, using the time slots computed in timing.py. Read this script as your
voice-over (a timestamped copy is in Script_with_timestamps.pdf).
"""

NARRATION = {
    "S0_Title": [
        "In this video, we'll see how Gaussian elimination solves "
        "a three by three system of equations, step by step.",
    ],
    "S1_Hook": [
        "Here are three equations in three unknowns. x plus y plus z equals six. "
        "Two x plus three y plus z equals eleven. And x minus y plus two z equals five.",
        "Guessing is hard, because every equation involves every variable.",
        "Geometrically, each equation is a plane in space, "
        "and a solution is a point lying on all three planes.",
        "Is there a systematic method, one a computer could follow, to find where they meet? "
        "Yes: Gaussian elimination.",
    ],
    "S2_Concept": [
        "We write the system as A x equals b: "
        "A holds the coefficients, x the unknowns, and b the right hand sides.",
        "Only the numbers matter, so we attach b to A, forming the augmented matrix. "
        "Each row is one equation.",
        "We are allowed three elementary row operations. Swap two rows. "
        "Multiply a row by a nonzero constant. "
        "Or replace a row by itself plus a multiple of another row.",
        "Our goal is row echelon form: a staircase, where each row's first nonzero entry, "
        "the pivot, sits right of the pivot above it, with zeros below every pivot.",
        "By the end, you'll be able to carry out elimination on a three by three system, "
        "and explain why it never changes the solution.",
    ],
    "S3_Intuition": [
        "Why are row operations allowed? Let's start in two dimensions. "
        "Take x plus y equals three, and two x minus y equals zero. "
        "These two lines cross at the point one, two.",
        "Now replace row two by row two minus two times row one. "
        "The x terms cancel, leaving minus three y equals minus six.",
        "Watch the second line. It rotates until it is horizontal, "
        "but it turns around the same intersection point. "
        "And adding two times row one back undoes the step.",
        "That is the whole idea: the picture gets simpler, while the answer stays the same. "
        "Swapping and scaling are reversible too, so the solution set is always preserved.",
    ],
    "S4_Elimination": [
        "Now, back to our three by three system. Here is its augmented matrix.",
        "Step one: the first pivot is the top left one. "
        "We use it to create zeros below it.",
        "Row two starts with a two, so we replace row two by row two minus two times row one. "
        "That gives zero, one, minus one, and eleven minus twelve, minus one.",
        "Row three starts with a one, so row three minus row one "
        "gives zero, minus two, one, and minus one.",
        "Column one is clear. Step two: move down and right, "
        "to the pivot in row two, column two.",
        "Below it is a minus two, so row three becomes row three plus two times row two: "
        "zero, zero, minus one, and minus three.",
        "That's row echelon form: pivots one, one, and minus one, "
        "in a staircase with zeros beneath them.",
    ],
    "S5_BackSub": [
        "Back as equations, the system is upper triangular. "
        "The last one says minus z equals minus three, so z equals three.",
        "Substitute upward: y minus z equals minus one, so y equals two.",
        "Then x equals six minus two minus three, which is one.",
        "Checking the original equations: six, eleven, and five. All three hold.",
    ],
    "S6_Interpretation": [
        "Geometrically, each row operation replaced one plane by a new plane "
        "through the same common point. The last one is now just the flat plane, z equals three.",
        "A pivot in every column means the planes meet in exactly one point: "
        "the unique solution, one, two, three.",
        "But a row like zero, zero, zero, bar, five says zero equals five: no solution.",
        "And if a column has no pivot, its variable is free, giving infinitely many solutions.",
    ],
    "S7_Summary": [
        "To summarize. One: row operations are reversible, so they never change the solution set. "
        "Two: pivots guide elimination, clearing entries below them to reach echelon form. "
        "Three: back substitution reads off the solution, and the pivots tell us if it is unique.",
        "Thanks for watching!",
    ],
}

SCENE_ORDER = list(NARRATION.keys())

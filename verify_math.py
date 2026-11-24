"""Independent check of every number shown in the video (exact fractions, no rounding)."""
from fractions import Fraction as F

A = [[1, 1, 1, 6], [2, 3, 1, 11], [1, -1, 2, 5]]
M = [[F(v) for v in r] for r in A]


def replace(M, i, c, j):
    """R_i <- R_i + c * R_j  (rows numbered from 1, as in the video)"""
    M[i - 1] = [a + c * b for a, b in zip(M[i - 1], M[j - 1])]


steps = [
    (2, -2, 1, [0, 1, -1, -1]),     # R2 <- R2 - 2 R1
    (3, -1, 1, [0, -2, 1, -1]),     # R3 <- R3 - 1 R1
    (3, 2, 2, [0, 0, -1, -3]),      # R3 <- R3 + 2 R2
]
for i, c, j, expected in steps:
    replace(M, i, c, j)
    assert M[i - 1] == expected, (i, M[i - 1])
    print(f"R{i} <- R{i} {'+' if c > 0 else '-'} {abs(c)}R{j}:  {[int(v) for v in M[i - 1]]}  ok")

# echelon form: pivots on the diagonal, zeros below
assert [M[k][k] for k in range(3)] == [1, 1, -1]
assert M[1][0] == M[2][0] == M[2][1] == 0
print("pivots:", [int(M[k][k]) for k in range(3)], "ok")

# back substitution
z = M[2][3] / M[2][2]
y = (M[1][3] - M[1][2] * z) / M[1][1]
x = (M[0][3] - M[0][1] * y - M[0][2] * z) / M[0][0]
assert (x, y, z) == (1, 2, 3)
print("solution (x, y, z) =", (int(x), int(y), int(z)), "ok")

# substitute into the ORIGINAL equations
for row in A:
    assert row[0] * x + row[1] * y + row[2] * z == row[3]
print("check in original equations ok")

# 2D intuition example: x + y = 3, 2x - y = 0, R2 <- R2 - 2R1 gives -3y = -6
r1, r2 = [1, 1, 3], [2, -1, 0]
new = [b - 2 * a for a, b in zip(r1, r2)]
assert new == [0, -3, -6]
# every line of the rotating family (2-2t)x + (-1-2t)y = -6t passes through (1, 2)
for k in range(11):
    t = F(k, 10)
    assert (2 - 2 * t) * 1 + (-1 - 2 * t) * 2 == -6 * t
print("2D example: new row", new, "and all intermediate lines pass through (1, 2) ok")

# planes after elimination contain (1, 2, 3)
assert 2 - 3 == -1 and -3 == -3
print("eliminated planes y - z = -1 and -z = -3 contain (1, 2, 3) ok")
print("ALL CHECKS PASSED")

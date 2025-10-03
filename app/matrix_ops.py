from typing import List

TOL = 1e-9

def is_close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol

def matrices_equal(A: List[List[float]], B: List[List[float]], tol: float = 1e-6) -> bool:
    if A is None or B is None:
        return False
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        return False
    for i in range(len(A)):
        for j in range(len(A[0])):
            if not is_close(A[i][j], B[i][j], tol):
                return False
    return True

def identity(n: int) -> List[List[float]]:
    I = [[0.0]*n for _ in range(n)]
    for i in range(n):
        I[i][i] = 1.0
    return I

def minor_matrix(A: List[List[float]], r: int, c: int) -> List[List[float]]:
    n = len(A)
    return [[A[i][j] for j in range(n) if j != c] for i in range(n) if i != r]

def det_recursive(A: List[List[float]]) -> float:
    n = len(A)
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0]*A[1][1] - A[0][1]*A[1][0]
    total = 0.0
    for j in range(n):
        total += (-1 if j % 2 else 1) * A[0][j] * det_recursive(minor_matrix(A, 0, j))
    return total

def cofactor_matrix(A: List[List[float]]) -> List[List[float]]:
    n = len(A)
    C = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            C[i][j] = (-1 if (i + j) % 2 else 1) * det_recursive(minor_matrix(A, i, j))
    return C

def transpose(A: List[List[float]]) -> List[List[float]]:
    return [list(row) for row in zip(*A)]

def inverse_by_adjugate(A: List[List[float]]) -> List[List[float]]:
    detA = det_recursive(A)
    if is_close(detA, 0.0):
        raise ZeroDivisionError("singular")
    C = cofactor_matrix(A)
    Adj = transpose(C)
    n = len(A)
    return [[Adj[i][j] / detA for j in range(n)] for i in range(n)]

def gauss_jordan_inverse(A: List[List[float]]) -> List[List[float]]:
    n = len(A)
    I = identity(n)
    AB = [A[i][:] + I[i][:] for i in range(n)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(AB[r][col]))
        if is_close(AB[pivot_row][col], 0.0):
            raise ZeroDivisionError("singular")
        if pivot_row != col:
            AB[col], AB[pivot_row] = AB[pivot_row], AB[col]
        pv = AB[col][col]
        for j in range(2 * n):
            AB[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            f = AB[r][col]
            if not is_close(f, 0.0):
                for j in range(2 * n):
                    AB[r][j] -= f * AB[col][j]
    return [row[n:] for row in AB]

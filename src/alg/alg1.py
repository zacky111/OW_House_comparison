import numpy as np

## Algorytm TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)


def _normalize(matrix, norm='l2'):
    """Normalize columns of matrix. Returns normalized matrix (same shape)."""
    X = np.asarray(matrix, dtype=float)
    if X.ndim != 2:
        raise ValueError("matrix must be 2D")
    if norm == 'l2':
        denom = np.sqrt((X ** 2).sum(axis=0))
        denom[denom == 0] = 1.0
        return X / denom
    elif norm == 'l1':
        denom = np.abs(X).sum(axis=0)
        denom[denom == 0] = 1.0
        return X / denom
    elif norm == 'range':
        mn = X.min(axis=0)
        mx = X.max(axis=0)
        rng = mx - mn
        rng[rng == 0] = 1.0
        return (X - mn) / rng
    else:
        raise ValueError("Unsupported norm")

def _distance(a, b, p='l2'):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diff = a - b
    if p == 'l2':
        return np.sqrt((diff ** 2).sum(axis=1))
    if p == 'l1':
        return np.abs(diff).sum(axis=1)
    if p == 'linf':
        return np.max(np.abs(diff), axis=1)
    raise ValueError("Unsupported metric")

def calculate_topsis_score(data, weights=None, norm='l2'):
    """
    Oblicza TOPSIS closeness coefficient dla wierszy macierzy.
    - data: 2D numpy array lub pandas.DataFrame (m x n)
    - weights: lista/array długości n lub None (równomierne wagi)
    - norm: normalizacja ('l2','l1','range')
    Zwraca listę (index, score) posortowaną malejąco po score.
    Uwaga: TOPSIS zakłada, że wyższe wartości są lepsze (benefit). Jeśli jakieś kryteria
    są cost-type (mniejsze lepsze), należy je wcześniej odwrócić.
    """
    A = np.asarray(data, dtype=float)
    if A.ndim != 2:
        raise ValueError("Input data must be 2D array")
    m, n = A.shape

    if weights is None:
        w = np.ones(n, dtype=float)
    else:
        w = np.asarray(weights, dtype=float)
        if w.size != n:
            raise ValueError("Length of weights must match number of criteria (columns)")

    # Normalizacja kolumn
    V = _normalize(A, norm=norm)

    # Zastosuj wagi (znormalizowane do sumy 1)
    if w.sum() == 0:
        w = np.ones_like(w)
    w = w / w.sum()
    V = V * w.reshape((1, -1))

    # Ideals (benefit): best = max, worst = min
    best = V.max(axis=0)
    worst = V.min(axis=0)

    d_best = _distance(V, best, p='l2')
    d_worst = _distance(V, worst, p='l2')

    denom = d_best + d_worst
    # unikamy dzielenia przez 0
    denom[denom == 0] = np.finfo(float).eps
    cc = d_worst / denom  # closeness coefficient 0..1 (wyższe lepsze)

    results = list(enumerate(cc))
    results.sort(key=lambda x: x[1], reverse=True)
    return results

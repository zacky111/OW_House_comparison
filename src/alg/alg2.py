import numpy as np

# ==========================================
# RSM – Reference Set Method
# (zbiór aspiracji i status-quo)
# ==========================================


def _normalize(matrix, method="range"):
    """
    Normalizacja kolumn macierzy.

    method:
    - 'range' : (x - min) / (max - min)
    """
    X = np.asarray(matrix, dtype=float)

    if X.ndim != 2:
        raise ValueError("Macierz musi być 2D")

    if method == "range":
        mn = X.min(axis=0)
        mx = X.max(axis=0)
        rng = mx - mn
        rng[rng == 0] = 1.0
        return (X - mn) / rng

    raise ValueError("Nieobsługiwana metoda normalizacji")


def _distance(X, ref, metric="l2"):
    """
    Odległość wielu punktów X od jednego punktu referencyjnego ref.
    """
    diff = X - ref

    if metric == "l2":
        return np.sqrt((diff ** 2).sum(axis=1))
    if metric == "l1":
        return np.abs(diff).sum(axis=1)
    if metric == "linf":
        return np.max(np.abs(diff), axis=1)

    raise ValueError("Nieobsługiwana metryka odległości")


def RSM_alg(data, weights=None, metric="l2", norm="range"):
    """
    Reference Set Method (RSM)

    Parametry:
    ----------
    data : array-like (m x n)
        Macierz decyzyjna (wszystkie kryteria typu benefit!)
    weights : array-like (n) lub None
        Wagi kryteriów
    metric : {'l2','l1','linf'}
        Metryka odległości
    norm : {'range'}
        Metoda normalizacji

    Zwraca:
    -------
    Listę (index, score) posortowaną malejąco
    """

    A = np.asarray(data, dtype=float)
    if A.ndim != 2:
        raise ValueError("Dane wejściowe muszą być macierzą 2D")

    m, n = A.shape

    # ===== WAGI =====
    if weights is None:
        w = np.ones(n, dtype=float)
    else:
        w = np.asarray(weights, dtype=float)
        if w.size != n:
            raise ValueError("Liczba wag musi odpowiadać liczbie kryteriów")

    if w.sum() == 0:
        w = np.ones_like(w)

    w = w / w.sum()

    # ===== NORMALIZACJA =====
    X = _normalize(A, method=norm)

    # ===== ZASTOSUJ WAGI =====
    Xw = X * w.reshape(1, -1)

    # ===== ZBIORY ODNIESIENIA =====
    R_plus = Xw.max(axis=0)   # punkt aspiracji
    R_minus = Xw.min(axis=0)  # status quo

    # ===== ODLEGŁOŚCI =====
    d_plus = _distance(Xw, R_plus, metric)
    d_minus = _distance(Xw, R_minus, metric)

    denom = d_plus + d_minus
    denom[denom == 0] = np.finfo(float).eps

    # ===== FUNKCJA SKORINGOWA =====
    score = d_minus / denom  # im wyżej, tym lepiej

    results = list(enumerate(score))
    results.sort(key=lambda x: x[1], reverse=True)

    return results

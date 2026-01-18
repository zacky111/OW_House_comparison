import numpy as np

## Algorytm RSM (Reference Set Method) do wielokryterialnej analizy decyzyjnej


def _normalize(matrix, method="range"):
    """
    Normalizacja kolumn:
    - range: (x - min) / (max - min)
    """
    X = np.asarray(matrix, dtype=float)
    mn = X.min(axis=0)
    mx = X.max(axis=0)
    rng = mx - mn
    rng[rng == 0] = 1.0
    return (X - mn) / rng


def _distance(X, ref, metric="l2"):
    """
    Odległość wielu punktów X od jednego punktu referencyjnego ref
    """
    diff = X - ref
    if metric == "l2":
        return np.sqrt((diff ** 2).sum(axis=1))
    if metric == "l1":
        return np.abs(diff).sum(axis=1)
    if metric == "linf":
        return np.max(np.abs(diff), axis=1)
    raise ValueError("Nieobsługiwana metryka")


def RSM_alg(data, weights=None, metric="l2"):
    """
    Algorytm RSM – klasyczny wariant zbiorów odniesienia (R⁺, R⁻)

    Parametry:
    - data: macierz m x n (numpy array lub DataFrame)
    - weights: lista wag (n) lub None
    - metric: 'l2', 'l1', 'linf'

    Zwraca:
    - listę (index, score) posortowaną malejąco
    """

    A = np.asarray(data, dtype=float)
    if A.ndim != 2:
        raise ValueError("Dane wejściowe muszą być macierzą 2D")

    m, n = A.shape

    # wagi
    if weights is None:
        w = np.ones(n)
    else:
        w = np.asarray(weights, dtype=float)
        if len(w) != n:
            raise ValueError("Długość wag musi zgadzać się z liczbą kryteriów")

    if w.sum() == 0:
        w = np.ones(n)
    w = w / w.sum()

    # normalizacja
    X = _normalize(A, method="range")

    # zastosuj wagi
    Xw = X * w.reshape(1, -1)

    # punkty odniesienia
    R_plus = Xw.max(axis=0)    # aspiracja
    R_minus = Xw.min(axis=0)   # status-quo

    # odległości
    d_plus = _distance(Xw, R_plus, metric)
    d_minus = _distance(Xw, R_minus, metric)

    denom = d_plus + d_minus
    denom[denom == 0] = np.finfo(float).eps

    # funkcja skoringowa RSM
    score = d_minus / denom

    results = list(enumerate(score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results
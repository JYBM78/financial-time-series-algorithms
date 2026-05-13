import numpy as np

def distancia_euclidiana(a, b):
    return np.sqrt(np.sum((np.array(a) - np.array(b)) ** 2))

def distancia_euclidiana_normalizada(a, b):
    return distancia_euclidiana(a, b) / max(np.sqrt(np.sum(np.array(a) ** 2)), 1e-10)

def euclidean_distance(a, b):
    return distancia_euclidiana(a, b)

def euclidean_distance_normalized(a, b):
    return distancia_euclidiana_normalizada(a, b)

def euclidean_similarity_score(a, b):
    dist = distancia_euclidiana(a, b)
    return 1.0 / (1.0 + dist)

def correlacion_pearson(a, b):
    x, y = np.array(a, dtype=float), np.array(b, dtype=float)
    n = len(x)
    mx, my = np.mean(x), np.mean(y)
    cov = np.sum((x - mx) * (y - my))
    var_x = np.sum((x - mx) ** 2)
    var_y = np.sum((y - my) ** 2)
    denom = np.sqrt(var_x * var_y)
    if denom == 0:
        return 0.0
    return cov / denom

def pearson_correlation(a, b):
    return correlacion_pearson(a, b)

def interpret_correlation(r):
    r = abs(r)
    if r >= 0.9:
        return "Correlacion muy fuerte"
    elif r >= 0.7:
        return "Correlacion fuerte"
    elif r >= 0.5:
        return "Correlacion moderada"
    elif r >= 0.3:
        return "Correlacion debil"
    else:
        return "Correlacion muy debil o nula"

def dynamic_time_warping(a, b):
    n, m = len(a), len(b)
    dtw = np.full((n + 1, m + 1), np.inf)
    dtw[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(a[i - 1] - b[j - 1])
            dtw[i, j] = cost + min(dtw[i - 1, j], dtw[i, j - 1], dtw[i - 1, j - 1])
    return dtw[n, m]

def dynamic_time_warping_normalized(a, b):
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0.0
    return dynamic_time_warping(a, b) / (n + m)

def dtw_similarity_score(a, b):
    dist = dynamic_time_warping(a, b)
    return 1.0 / (1.0 + dist)

def get_dtw_path(a, b):
    n, m = len(a), len(b)
    dtw = np.full((n + 1, m + 1), np.inf)
    dtw[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(a[i - 1] - b[j - 1])
            dtw[i, j] = cost + min(dtw[i - 1, j], dtw[i, j - 1], dtw[i - 1, j - 1])
    path = []
    i, j = n, m
    while i > 0 or j > 0:
        path.append((i - 1, j - 1))
        if i == 0:
            j -= 1
        elif j == 0:
            i -= 1
        else:
            idx = np.argmin([dtw[i - 1, j], dtw[i, j - 1], dtw[i - 1, j - 1]])
            if idx == 0:
                i -= 1
            elif idx == 1:
                j -= 1
            else:
                i -= 1
                j -= 1
    path.reverse()
    return path

def similitud_coseno(a, b):
    x, y = np.array(a, dtype=float), np.array(b, dtype=float)
    dot = np.dot(x, y)
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)
    if norm_x == 0 or norm_y == 0:
        return 0.0
    return dot / (norm_x * norm_y)

def cosine_similarity(a, b):
    return similitud_coseno(a, b)

def distancia_coseno(a, b):
    return 1.0 - similitud_coseno(a, b)

def cosine_angle(a, b):
    sim = similitud_coseno(a, b)
    sim = np.clip(sim, -1.0, 1.0)
    return np.degrees(np.arccos(sim))

def interpret_cosine_similarity(sim):
    if sim >= 0.9:
        return "Angulo muy pequeno (casi identicos)"
    elif sim >= 0.7:
        return "Angulo pequeno (alta similitud)"
    elif sim >= 0.5:
        return "Angulo moderado"
    elif sim >= 0.0:
        return "Angulo considerable"
    else:
        return "Direcciones opuestas"

def calcular_todas_similitudes(a, b):
    return {
        "distancia_euclidiana": distancia_euclidiana(a, b),
        "distancia_euclidiana_normalizada": distancia_euclidiana_normalizada(a, b),
        "correlacion_pearson": correlacion_pearson(a, b),
        "dtw": dynamic_time_warping(a, b),
        "similitud_coseno": similitud_coseno(a, b),
        "distancia_coseno": distancia_coseno(a, b),
    }

def comparar_activos(df, ticker1, ticker2, columna="Close"):
    df1 = df[df["Ticker"] == ticker1].sort_values("Date")
    df2 = df[df["Ticker"] == ticker2].sort_values("Date")
    merged = df1[["Date", columna]].merge(df2[["Date", columna]], on="Date", suffixes=("_1", "_2"))
    serie1 = merged[f"{columna}_1"].values
    serie2 = merged[f"{columna}_2"].values
    ret1 = np.diff(serie1) / serie1[:-1]
    ret2 = np.diff(serie2) / serie2[:-1]
    ret1 = ret1[np.isfinite(ret1)]
    ret2 = ret2[np.isfinite(ret2)]
    resultado = calcular_todas_similitudes(ret1, ret2)
    resultado["ticker1"] = ticker1
    resultado["ticker2"] = ticker2
    resultado["tipo_datos"] = f"Retornos diarios ({columna})"
    return resultado

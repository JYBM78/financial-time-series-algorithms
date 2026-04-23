"""
Multiplicación de Matrices Grandes - Seguimiento 2
Universidad del Quindío - Ingeniería de Sistemas y Computación
Implementación de 15 algoritmos con medición de tiempo de ejecución
"""

import numpy as np
import time
import json
import os
import math
import csv
import pickle
from concurrent.futures import ThreadPoolExecutor
import threading
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────
# GENERACIÓN Y PERSISTENCIA DE CASOS DE PRUEBA
# ─────────────────────────────────────────────────

def generar_matriz(n, seed=None):
    """Genera matriz n×n con números de mínimo 6 dígitos (100000–999999)."""
    rng = np.random.default_rng(seed)
    return rng.integers(100_000, 1_000_000, size=(n, n), dtype=np.int64)

def guardar_caso(nombre, A, B):
    path = f"casos/{nombre}"
    os.makedirs(path, exist_ok=True)
    np.save(f"{path}/A.npy", A)
    np.save(f"{path}/B.npy", B)
    print(f"  Caso guardado: {path}  ({A.shape[0]}×{A.shape[0]})")

def cargar_caso(nombre):
    path = f"casos/{nombre}"
    A = np.load(f"{path}/A.npy")
    B = np.load(f"{path}/B.npy")
    return A, B

def preparar_casos(n1, n2):
    """
    Prepara 2 casos de prueba. n debe ser factor de 2^k (requerimiento).
    Caso 1: n1×n1   Caso 2: n2×n2
    """
    import shutil
    
    os.makedirs("casos", exist_ok=True)
    
    # Verificar si los tamaños actuales coinciden con lo solicitado
    caso1_path = "casos/caso1"
    caso2_path = "casos/caso2"
    
    # Si existen pero los tamaños no coinciden, limpiar todo
    tamaños_correctos = True
    if os.path.exists(f"{caso1_path}/A.npy"):
        A1_exist = np.load(f"{caso1_path}/A.npy")
        if A1_exist.shape[0] != n1:
            tamaños_correctos = False
    if os.path.exists(f"{caso2_path}/A.npy"):
        A2_exist = np.load(f"{caso2_path}/A.npy")
        if A2_exist.shape[0] != n2:
            tamaños_correctos = False
    
    # Si algo está mal, limpiar carpeta completa
    if not tamaños_correctos and os.path.exists("casos"):
        print(f"  ⚠ Tamaños detectados no coinciden. Limpiando carpeta 'casos/'...")
        shutil.rmtree("casos")
        os.makedirs("casos", exist_ok=True)
    
    # Ahora generar/cargar con los tamaños correctos
    for nombre, n, seed in [("caso1", n1, 42), ("caso2", n2, 99)]:
        path = f"casos/{nombre}"
        A_path = f"{path}/A.npy"
        B_path = f"{path}/B.npy"
        
        if not os.path.exists(A_path) or not os.path.exists(B_path):
            print(f"  Generando {nombre} ({n}×{n})...")
            A = generar_matriz(n, seed)
            B = generar_matriz(n, seed + 1)
            guardar_caso(nombre, A, B)
        else:
            print(f"  {nombre} ya existe con tamaño ({n}×{n}), cargando...")
    
    return cargar_caso("caso1"), cargar_caso("caso2")


# ─────────────────────────────────────────────────
# 1. NaivOnArray  — O(n³)
# ─────────────────────────────────────────────────
def naiv_on_array(A, B):
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    return C


# ─────────────────────────────────────────────────
# 2. NaivLoopUnrollingTwo  — O(n³)
# ─────────────────────────────────────────────────
def naiv_loop_unrolling_two(A, B):
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            s = 0
            k = 0
            while k < n - 1:        # desenrollado ×2
                s += A[i, k] * B[k, j] + A[i, k+1] * B[k+1, j]
                k += 2
            if k < n:
                s += A[i, k] * B[k, j]
            C[i, j] = s
    return C


# ─────────────────────────────────────────────────
# 3. NaivLoopUnrollingFour  — O(n³)
# ─────────────────────────────────────────────────
def naiv_loop_unrolling_four(A, B):
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            s = 0
            k = 0
            while k < n - 3:        # desenrollado ×4
                s += (A[i, k]   * B[k,   j]
                    + A[i, k+1] * B[k+1, j]
                    + A[i, k+2] * B[k+2, j]
                    + A[i, k+3] * B[k+3, j])
                k += 4
            while k < n:
                s += A[i, k] * B[k, j]
                k += 1
            C[i, j] = s
    return C


# ─────────────────────────────────────────────────
# 4. WinogradOriginal  — O(n³)  (reduce mult por precómputo)
# ─────────────────────────────────────────────────
def winograd_original(A, B):
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    row_factor = np.zeros(n, dtype=np.int64)
    col_factor = np.zeros(n, dtype=np.int64)

    half = n // 2
    for i in range(n):
        for j in range(half):
            row_factor[i] += A[i, 2*j] * A[i, 2*j+1]
    for j in range(n):
        for i in range(half):
            col_factor[j] += B[2*i, j] * B[2*i+1, j]

    for i in range(n):
        for j in range(n):
            s = -row_factor[i] - col_factor[j]
            for k in range(half):
                s += (A[i, 2*k] + B[2*k+1, j]) * (A[i, 2*k+1] + B[2*k, j])
            C[i, j] = s
    if n % 2 == 1:
        for i in range(n):
            for j in range(n):
                C[i, j] += A[i, n-1] * B[n-1, j]
    return C


# ─────────────────────────────────────────────────
# 5. WinogradScaled  — O(n³)  (Winograd + escalado)
# ─────────────────────────────────────────────────
def winograd_scaled(A, B):
    """
    Versión escalada de Winograd: escala filas de A y columnas de B
    por el máximo absoluto para mejorar la estabilidad numérica.
    En enteros usamos la misma estructura pero escalamos a float64.
    """
    A_f = A.astype(np.float64)
    B_f = B.astype(np.float64)
    n = A_f.shape[0]

    row_scale = np.max(np.abs(A_f), axis=1, keepdims=True)
    row_scale[row_scale == 0] = 1
    col_scale = np.max(np.abs(B_f), axis=0, keepdims=True)
    col_scale[col_scale == 0] = 1

    A_s = A_f / row_scale
    B_s = B_f / col_scale

    half = n // 2
    row_factor = np.zeros(n)
    col_factor = np.zeros(n)
    for i in range(n):
        for j in range(half):
            row_factor[i] += A_s[i, 2*j] * A_s[i, 2*j+1]
    for j in range(n):
        for i in range(half):
            col_factor[j] += B_s[2*i, j] * B_s[2*i+1, j]

    C = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            s = -row_factor[i] - col_factor[j]
            for k in range(half):
                s += (A_s[i, 2*k] + B_s[2*k+1, j]) * (A_s[i, 2*k+1] + B_s[2*k, j])
            C[i, j] = s
    if n % 2 == 1:
        for i in range(n):
            for j in range(n):
                C[i, j] += A_s[i, n-1] * B_s[n-1, j]

    scale_matrix = row_scale * col_scale
    C = (C * scale_matrix).astype(np.int64)
    return C


# ─────────────────────────────────────────────────
# 6. StrassenNaiv  — O(n^2.807)
# ─────────────────────────────────────────────────
def strassen_naiv(A, B, threshold=64):
    n = A.shape[0]
    if n <= threshold:
        return A @ B   # numpy BLAS para la hoja recursiva

    # Rellenar hasta potencia de 2
    m = 1
    while m < n:
        m *= 2
    A_p = np.zeros((m, m), dtype=A.dtype)
    B_p = np.zeros((m, m), dtype=B.dtype)
    A_p[:n, :n] = A
    B_p[:n, :n] = B

    C_p = _strassen_rec(A_p, B_p, threshold)
    return C_p[:n, :n]

def _strassen_rec(A, B, threshold):
    n = A.shape[0]
    if n <= threshold:
        return A @ B
    half = n // 2
    A11, A12 = A[:half, :half], A[:half, half:]
    A21, A22 = A[half:, :half], A[half:, half:]
    B11, B12 = B[:half, :half], B[:half, half:]
    B21, B22 = B[half:, :half], B[half:, half:]

    M1 = _strassen_rec(A11 + A22, B11 + B22, threshold)
    M2 = _strassen_rec(A21 + A22, B11,        threshold)
    M3 = _strassen_rec(A11,        B12 - B22,  threshold)
    M4 = _strassen_rec(A22,        B21 - B11,  threshold)
    M5 = _strassen_rec(A11 + A12, B22,         threshold)
    M6 = _strassen_rec(A21 - A11, B11 + B12,   threshold)
    M7 = _strassen_rec(A12 - A22, B21 + B22,   threshold)

    C = np.empty_like(A)
    C[:half, :half] = M1 + M4 - M5 + M7
    C[:half, half:] = M3 + M5
    C[half:, :half] = M2 + M4
    C[half:, half:] = M1 - M2 + M3 + M6
    return C


# ─────────────────────────────────────────────────
# 7. StrassenWinograd  — O(n^2.807)  (menos adiciones)
# ─────────────────────────────────────────────────
def strassen_winograd(A, B, threshold=64):
    n = A.shape[0]
    if n <= threshold:
        return A @ B
    m = 1
    while m < n:
        m *= 2
    A_p = np.zeros((m, m), dtype=A.dtype)
    B_p = np.zeros((m, m), dtype=B.dtype)
    A_p[:n, :n] = A
    B_p[:n, :n] = B
    C_p = _sw_rec(A_p, B_p, threshold)
    return C_p[:n, :n]

def _sw_rec(A, B, threshold):
    n = A.shape[0]
    if n <= threshold:
        return A @ B
    half = n // 2
    A11, A12 = A[:half, :half], A[:half, half:]
    A21, A22 = A[half:, :half], A[half:, half:]
    B11, B12 = B[:half, :half], B[:half, half:]
    B21, B22 = B[half:, :half], B[half:, half:]

    S1  = A21 + A22
    S2  = S1  - A11
    S3  = A11 - A21
    S4  = A12 - S2
    S5  = B12 - B11
    S6  = B22 - S5
    S7  = B22 - B12
    S8  = S6  - B21

    M1 = _sw_rec(S2,  S6,  threshold)
    M2 = _sw_rec(A11, B11, threshold)
    M3 = _sw_rec(A12, B21, threshold)
    M4 = _sw_rec(S3,  S7,  threshold)
    M5 = _sw_rec(S1,  S5,  threshold)
    M6 = _sw_rec(S4,  B22, threshold)
    M7 = _sw_rec(A22, S8,  threshold)

    T1 = M1 + M2
    T2 = T1 + M4

    C = np.empty_like(A)
    C[:half, :half] = M2 + M3
    C[:half, half:] = T1 + M5 + M6
    C[half:, :half] = T2 - M7
    C[half:, half:] = T2 + M5
    return C


# ─────────────────────────────────────────────────
# 8–10. III: Row×Column  (sequential block / parallel block / enhanced parallel block)
# ─────────────────────────────────────────────────
def iii3_sequential_block(A, B, bsize=64):
    """III.3 - Row by Column Sequential Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    for i1 in range(0, n, bsize):
        for j1 in range(0, n, bsize):
            for k1 in range(0, n, bsize):
                i_end = min(i1 + bsize, n)
                j_end = min(j1 + bsize, n)
                k_end = min(k1 + bsize, n)
                C[i1:i_end, j1:j_end] += A[i1:i_end, k1:k_end] @ B[k1:k_end, j1:j_end]
    return C

def iii4_parallel_block(A, B, bsize=64):
    """III.4 - Row by Column Parallel Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    lock = threading.Lock()

    def compute_block(i1):
        local = np.zeros((n, n), dtype=np.int64)
        for j1 in range(0, n, bsize):
            for k1 in range(0, n, bsize):
                i_end = min(i1 + bsize, n)
                j_end = min(j1 + bsize, n)
                k_end = min(k1 + bsize, n)
                local[i1:i_end, j1:j_end] += A[i1:i_end, k1:k_end] @ B[k1:k_end, j1:j_end]
        with lock:
            C[:] += local

    with ThreadPoolExecutor() as ex:
        ex.map(compute_block, range(0, n, bsize))
    return C

def iii5_enhanced_parallel_block(A, B, bsize=64):
    """III.5 - Row by Column Enhanced Parallel Block (mitades)"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    lock = threading.Lock()

    def half_work(i_start, i_stop):
        local = np.zeros((n, n), dtype=np.int64)
        for i1 in range(i_start, i_stop, bsize):
            for j1 in range(0, n, bsize):
                for k1 in range(0, n, bsize):
                    i_end = min(i1 + bsize, n)
                    j_end = min(j1 + bsize, n)
                    k_end = min(k1 + bsize, n)
                    local[i1:i_end, j1:j_end] += A[i1:i_end, k1:k_end] @ B[k1:k_end, j1:j_end]
        with lock:
            C[:] += local

    mid = n // 2
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(half_work, 0, mid)
        f2 = ex.submit(half_work, mid, n)
        f1.result(); f2.result()
    return C


# ─────────────────────────────────────────────────
# 11–13. IV: Row×Row  (sequential block / parallel block / enhanced parallel block)
# ─────────────────────────────────────────────────
def iv3_sequential_block(A, B, bsize=64):
    """IV.3 - Row by Row Sequential Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    for i1 in range(0, n, bsize):
        for j1 in range(0, n, bsize):
            for k1 in range(0, n, bsize):
                i_end = min(i1 + bsize, n)
                j_end = min(j1 + bsize, n)
                k_end = min(k1 + bsize, n)
                # A[i,k] += B[i,j]*C[j,k]  → A_local = B_block @ C_block
                C[i1:i_end, k1:k_end] += A[i1:i_end, j1:j_end] @ B[j1:j_end, k1:k_end]
    return C

def iv4_parallel_block(A, B, bsize=64):
    """IV.4 - Row by Row Parallel Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    lock = threading.Lock()

    def compute_block(i1):
        local = np.zeros((n, n), dtype=np.int64)
        for j1 in range(0, n, bsize):
            for k1 in range(0, n, bsize):
                i_end = min(i1 + bsize, n)
                j_end = min(j1 + bsize, n)
                k_end = min(k1 + bsize, n)
                local[i1:i_end, k1:k_end] += A[i1:i_end, j1:j_end] @ B[j1:j_end, k1:k_end]
        with lock:
            C[:] += local

    with ThreadPoolExecutor() as ex:
        ex.map(compute_block, range(0, n, bsize))
    return C

def iv5_enhanced_parallel_block(A, B, bsize=64):
    """IV.5 - Row by Row Enhanced Parallel Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    lock = threading.Lock()

    def half_work(i_start, i_stop):
        local = np.zeros((n, n), dtype=np.int64)
        for i1 in range(i_start, i_stop, bsize):
            for j1 in range(0, n, bsize):
                for k1 in range(0, n, bsize):
                    i_end = min(i1 + bsize, n)
                    j_end = min(j1 + bsize, n)
                    k_end = min(k1 + bsize, n)
                    local[i1:i_end, k1:k_end] += A[i1:i_end, j1:j_end] @ B[j1:j_end, k1:k_end]
        with lock:
            C[:] += local

    mid = n // 2
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(half_work, 0, mid)
        f2 = ex.submit(half_work, mid, n)
        f1.result(); f2.result()
    return C


# ─────────────────────────────────────────────────
# 14–15. V: Column×Column  (sequential block / parallel block)
# ─────────────────────────────────────────────────
def v3_sequential_block(A, B, bsize=64):
    """V.3 - Column by Column Sequential Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    for i1 in range(0, n, bsize):
        for j1 in range(0, n, bsize):
            for k1 in range(0, n, bsize):
                i_end = min(i1 + bsize, n)
                j_end = min(j1 + bsize, n)
                k_end = min(k1 + bsize, n)
                # A[k,i] += B[k,j]*C[j,i]
                C[k1:k_end, i1:i_end] += A[k1:k_end, j1:j_end] @ B[j1:j_end, i1:i_end]
    return C

def v4_parallel_block(A, B, bsize=64):
    """V.4 - Column by Column Parallel Block"""
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    lock = threading.Lock()

    def compute_block(i1):
        local = np.zeros((n, n), dtype=np.int64)
        for j1 in range(0, n, bsize):
            for k1 in range(0, n, bsize):
                i_end = min(i1 + bsize, n)
                j_end = min(j1 + bsize, n)
                k_end = min(k1 + bsize, n)
                local[k1:k_end, i1:i_end] += A[k1:k_end, j1:j_end] @ B[j1:j_end, i1:i_end]
        with lock:
            C[:] += local

    with ThreadPoolExecutor() as ex:
        ex.map(compute_block, range(0, n, bsize))
    return C


# ─────────────────────────────────────────────────
# EJECUTOR CON MEDICIÓN DE TIEMPO
# ─────────────────────────────────────────────────

ALGORITMOS = [
    ("NaivOnArray",               naiv_on_array),
    ("NaivLoopUnrollingTwo",      naiv_loop_unrolling_two),
    ("NaivLoopUnrollingFour",     naiv_loop_unrolling_four),
    ("WinogradOriginal",          winograd_original),
    ("WinogradScaled",            winograd_scaled),
    ("StrassenNaiv",              strassen_naiv),
    ("StrassenWinograd",          strassen_winograd),
    ("III.3 Sequential Block",    iii3_sequential_block),
    ("III.4 Parallel Block",      iii4_parallel_block),
    ("III.5 Enhanced Par Block",  iii5_enhanced_parallel_block),
    ("IV.3 Sequential Block",     iv3_sequential_block),
    ("IV.4 Parallel Block",       iv4_parallel_block),
    ("IV.5 Enhanced Par Block",   iv5_enhanced_parallel_block),
    ("V.3 Sequential Block",      v3_sequential_block),
    ("V.4 Parallel Block",        v4_parallel_block),
]

COMPLEJIDADES = {
    "NaivOnArray":              "O(n³)",
    "NaivLoopUnrollingTwo":     "O(n³)",
    "NaivLoopUnrollingFour":    "O(n³)",
    "WinogradOriginal":         "O(n³)",
    "WinogradScaled":           "O(n³)",
    "StrassenNaiv":             "O(n^2.807)",
    "StrassenWinograd":         "O(n^2.807)",
    "III.3 Sequential Block":   "O(n³)",
    "III.4 Parallel Block":     "O(n³/p)",
    "III.5 Enhanced Par Block": "O(n³/p)",
    "IV.3 Sequential Block":    "O(n³)",
    "IV.4 Parallel Block":      "O(n³/p)",
    "IV.5 Enhanced Par Block":  "O(n³/p)",
    "V.3 Sequential Block":     "O(n³)",
    "V.4 Parallel Block":       "O(n³/p)",
}


def ejecutar_algoritmos(A, B, caso_nombre, usar_naiv_puro=True):
    """Ejecuta todos los algoritmos y retorna resultados con tiempos en ms."""
    n = A.shape[0]
    resultados = {}

    # Límite para algoritmos O(n³) puros en Python (muy lentos)
    # CRITERIO DE OMISIÓN: "lento" = algoritmos con complejidad O(n³) que exceden
    # el límite de tamaño n. Con n > 64, estos algoritmos tomarían más de 60 segundos
    # en matrices de 512x512 y más de 8 minutos en 1024x1024, haciéndolos imprácticos.
    # Por ejemplo: NaivOnArray con n=512 toma ~123 segundos vs Strassen que toma ~0.2 segundos.
    LIMITE_NAIV = 64   # si n > LIMITE_NAIV, los naiv puros se omiten

    for nombre, func in ALGORITMOS:
        es_naiv_puro = nombre in ("NaivOnArray", "NaivLoopUnrollingTwo",
                                  "NaivLoopUnrollingFour", "WinogradOriginal",
                                  "WinogradScaled")

        if es_naiv_puro and n > LIMITE_NAIV and not usar_naiv_puro:
            print(f"  [{caso_nombre}] {nombre:30s}  OMITIDO (n={n} > {LIMITE_NAIV})")
            resultados[nombre] = None
            continue

        print(f"  [{caso_nombre}] {nombre:30s} ...", end="", flush=True)
        t0 = time.perf_counter()
        C = func(A, B)
        t1 = time.perf_counter()
        ms = (t1 - t0) * 1000
        print(f"  {ms:10.3f} ms")
        resultados[nombre] = round(ms, 4)

    return resultados


def guardar_resultados(resultados_c1, n1, resultados_c2, n2):
    # Crear directorio de persistencia
    persist_dir = "persistencia"
    os.makedirs(persist_dir, exist_ok=True)
    
    data = {
        "caso1": {"n": n1, "tiempos_ms": resultados_c1},
        "caso2": {"n": n2, "tiempos_ms": resultados_c2},
        "complejidades": COMPLEJIDADES,
    }
    
    # Guardar en JSON
    json_path = f"{persist_dir}/resultados.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ JSON guardado: {json_path}")
    
    # Guardar en Pickle (binario más robusto)
    pickle_path = f"{persist_dir}/resultados.pkl"
    with open(pickle_path, "wb") as f:
        pickle.dump(data, f)
    print(f"✓ Pickle guardado: {pickle_path}")
    
    # Guardar en CSV (formato tabular)
    csv_path = f"{persist_dir}/resultados.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Algoritmo", f"Caso1 (n={n1})", f"Caso2 (n={n2})", "Complejidad"])
        for nombre in [algo[0] for algo in ALGORITMOS]:
            t1 = resultados_c1.get(nombre)
            t2 = resultados_c2.get(nombre)
            comp = COMPLEJIDADES.get(nombre, "?")
            t1_str = f"{t1:.4f}" if t1 is not None else "OMITIDO"
            t2_str = f"{t2:.4f}" if t2 is not None else "OMITIDO"
            writer.writerow([nombre, t1_str, t2_str, comp])
    print(f"✓ CSV guardado: {csv_path}")


def visualizar_resultados(resultados_c1, n1, resultados_c2, n2):
    """Genera diagramas de barras comparativos para los tiempos de ejecución (todos los 15 algoritmos)."""
    persist_dir = "persistencia"
    
    # Obtener todos los nombres de algoritmos (15 totales)
    todos_algoritmos = [name for name, _ in ALGORITMOS]
    
    # Preparar datos para Caso 1
    times_c1 = []
    omitidos_c1 = []
    for name in todos_algoritmos:
        val = resultados_c1.get(name)
        omitidos_c1.append(val is None)
        times_c1.append(val if val is not None else 0.1)  # Small value for log scale
    
    # Preparar datos para Caso 2
    times_c2 = []
    omitidos_c2 = []
    for name in todos_algoritmos:
        val = resultados_c2.get(name)
        omitidos_c2.append(val is None)
        times_c2.append(val if val is not None else 0.1)  # Small value for log scale
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 7))
    
    # Función auxiliar para determinar color
    def get_color(name, omitido):
        if omitido:
            return '#cccccc'  # Gris claro para omitidos
        elif COMPLEJIDADES.get(name, '').startswith('O(n^2'):
            return '#1f77b4'  # Azul para Strassen
        else:
            return '#ff7f0e'  # Naranja para otros
    
    # Gráfico Caso 1
    colors1 = [get_color(name, omitidos_c1[i]) for i, name in enumerate(todos_algoritmos)]
    bars1 = ax1.bar(range(len(todos_algoritmos)), times_c1, color=colors1, edgecolor='black', alpha=0.85)
    ax1.set_xlabel("Algoritmo", fontsize=11, fontweight='bold')
    ax1.set_ylabel("Tiempo (ms)", fontsize=11, fontweight='bold')
    ax1.set_title(f"Caso 1 - Matrices {n1}×{n1}", fontsize=12, fontweight='bold')
    ax1.set_yscale('log')
    ax1.set_xticks(range(len(todos_algoritmos)))
    ax1.set_xticklabels(todos_algoritmos, rotation=45, ha='right', fontsize=8.5)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Agregar etiqueta "OMITIDO" sobre barras omitidas en Caso 1
    for i, omitido in enumerate(omitidos_c1):
        if omitido:
            ax1.text(i, 0.15, 'OMITIDO', ha='center', va='bottom', fontsize=7, style='italic', color='#666666')
    
    # Gráfico Caso 2
    colors2 = [get_color(name, omitidos_c2[i]) for i, name in enumerate(todos_algoritmos)]
    bars2 = ax2.bar(range(len(todos_algoritmos)), times_c2, color=colors2, edgecolor='black', alpha=0.85)
    ax2.set_xlabel("Algoritmo", fontsize=11, fontweight='bold')
    ax2.set_ylabel("Tiempo (ms)", fontsize=11, fontweight='bold')
    ax2.set_title(f"Caso 2 - Matrices {n2}×{n2}", fontsize=12, fontweight='bold')
    ax2.set_yscale('log')
    ax2.set_xticks(range(len(todos_algoritmos)))
    ax2.set_xticklabels(todos_algoritmos, rotation=45, ha='right', fontsize=8.5)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Agregar etiqueta "OMITIDO" sobre barras omitidas en Caso 2
    for i, omitido in enumerate(omitidos_c2):
        if omitido:
            ax2.text(i, 0.15, 'OMITIDO', ha='center', va='bottom', fontsize=7, style='italic', color='#666666')
    
    # Agregar leyenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#1f77b4', alpha=0.85, edgecolor='black', label='Strassen O(n^2.807)'),
        Patch(facecolor='#ff7f0e', alpha=0.85, edgecolor='black', label='Otros O(n³) / Paralelos'),
        Patch(facecolor='#cccccc', alpha=0.85, edgecolor='black', label='Omitido (muy lento)')
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=10)
    
    plt.tight_layout()
    
    # Guardar figura
    chart_path = f"{persist_dir}/benchmark_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    print(f"✓ Gráfico guardado: {chart_path} (15 algoritmos totales)")
    
    # Mostrar (opcional)
    # plt.show()


# ─────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────
if __name__ == "__main__":
    # Tamaños: deben ser factor de 2^k. Usamos 128 y 256
    N1, N2 = 512, 1024

    print("=" * 60)
    print("PREPARANDO CASOS DE PRUEBA")
    print("=" * 60)
    (A1, B1), (A2, B2) = preparar_casos(N1, N2)
    print(f"  Caso 1: {A1.shape}  |  Caso 2: {A2.shape}\n")

    print("=" * 60)
    print(f"EJECUTANDO ALGORITMOS — CASO 1 (n={N1})")
    print("=" * 60)
    r1 = ejecutar_algoritmos(A1, B1, "caso1", usar_naiv_puro=True)

    print("\n" + "=" * 60)
    print(f"EJECUTANDO ALGORITMOS — CASO 2 (n={N2})")
    print("=" * 60)
    # Para n=256 los naiv puros en Python tardarían horas; los marcamos None
    r2 = ejecutar_algoritmos(A2, B2, "caso2", usar_naiv_puro=False)

    print("\n" + "=" * 60)
    print("GUARDANDO RESULTADOS")
    print("=" * 60)
    guardar_resultados(r1, N1, r2, N2)
    
    print("\n" + "=" * 60)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 60)
    visualizar_resultados(r1, N1, r2, N2)
    
    print("\n✓ Ejecución completada.")
"""Pruebas unitarias para los algoritmos de similitud."""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.similarity import (
    euclidean_distance, euclidean_distance_normalized, euclidean_similarity_score,
    pearson_correlation, interpret_correlation,
    dynamic_time_warping, dynamic_time_warping_normalized, get_dtw_path, dtw_similarity_score,
    cosine_similarity, cosine_angle, interpret_cosine_similarity,
)


def test_euclidean_distance():
    """Prueba distancia euclidiana."""
    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]

    dist = euclidean_distance(a, b)
    assert abs(dist - 5.196152) < 1e-5, f"Esperado ~5.196, obtenido {dist}"

    dist_same = euclidean_distance(a, a)
    assert dist_same == 0.0, f"Distancia de serie consigo misma debe ser 0, obtenido {dist_same}"

    dist_norm = euclidean_distance_normalized(a, b)
    expected_norm = 3.0
    assert abs(dist_norm - expected_norm) < 1e-5, f"Esperado ~{expected_norm}, obtenido {dist_norm}"

    sim = euclidean_similarity_score(a, b)
    assert 0 <= sim <= 1, f"Similitud debe estar en [0, 1], obtenido {sim}"

    print("  [OK] Distancia Euclidiana")


def test_pearson_correlation():
    """Prueba correlacion de Pearson."""
    a = [1.0, 2.0, 3.0, 4.0, 5.0]
    b = [2.0, 4.0, 6.0, 8.0, 10.0]

    r = pearson_correlation(a, b)
    assert abs(r - 1.0) < 1e-10, f"Correlacion de series proporcionales debe ser 1, obtenido {r}"

    c = [5.0, 4.0, 3.0, 2.0, 1.0]
    r_neg = pearson_correlation(a, c)
    assert abs(r_neg - (-1.0)) < 1e-10, f"Correlacion negativa perfecta debe ser -1, obtenido {r_neg}"

    interp = interpret_correlation(r)
    assert isinstance(interp, str)

    print("  [OK] Correlacion de Pearson")


def test_dtw():
    """Prueba Dynamic Time Warping."""
    a = [1.0, 2.0, 3.0]
    b = [1.0, 2.0, 3.0]

    dist = dynamic_time_warping(a, b)
    assert dist == 0.0, f"DTW de series identicas debe ser 0, obtenido {dist}"

    c = [1.0, 3.0]
    dist_diff_len = dynamic_time_warping(a, c)
    assert dist_diff_len >= 0, f"DTW debe ser no negativo, obtenido {dist_diff_len}"

    camino = get_dtw_path(a, b)
    assert len(camino) > 0
    assert camino[0] == (0, 0), f"Camino debe iniciar en (0, 0), obtenido {camino[0]}"
    assert camino[-1] == (2, 2), f"Camino debe terminar en (2, 2), obtenido {camino[-1]}"

    sim = dtw_similarity_score(a, b)
    assert abs(sim - 1.0) < 1e-10, f"Similitud DTW de series identicas debe ser 1, obtenido {sim}"

    print("  [OK] Dynamic Time Warping")


def test_cosine_similarity():
    """Prueba similitud por coseno."""
    a = [1.0, 2.0, 3.0]
    b = [2.0, 4.0, 6.0]

    cos = cosine_similarity(a, b)
    assert abs(cos - 1.0) < 1e-10, f"Coseno de vectores proporcionales debe ser 1, obtenido {cos}"

    c = [-1.0, -2.0, -3.0]
    cos_neg = cosine_similarity(a, c)
    assert abs(cos_neg - (-1.0)) < 1e-10, f"Coseno de vectores opuestos debe ser -1, obtenido {cos_neg}"

    angulo = cosine_angle(a, b)
    assert abs(angulo - 0.0) < 1e-5, f"Angulo de vectores proporcionales debe ser 0, obtenido {angulo}"

    interp = interpret_cosine_similarity(cos)
    assert isinstance(interp, str)

    print("  [OK] Similitud por Coseno")


def test_error_handling():
    """Prueba manejo de errores."""
    a = [1.0, 2.0]
    b = [1.0]

    try:
        euclidean_distance(a, b)
        assert False, "Debio lanzar ValueError"
    except ValueError:
        pass

    try:
        pearson_correlation(a, b)
        assert False, "Debio lanzar ValueError"
    except ValueError:
        pass

    try:
        cosine_similarity(a, b)
        assert False, "Debio lanzar ValueError"
    except ValueError:
        pass

    print("  [OK] Manejo de errores")


if __name__ == "__main__":
    print("Ejecutando pruebas de algoritmos de similitud...\n")
    test_euclidean_distance()
    test_pearson_correlation()
    test_dtw()
    test_cosine_similarity()
    test_error_handling()
    print("\nTodas las pruebas pasaron!")

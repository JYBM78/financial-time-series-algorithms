"""Modulo de algoritmos de similitud de series de tiempo financieras.

Proporciona implementaciones de:
    - Distancia Euclidiana
    - Correlacion de Pearson
    - Dynamic Time Warping (DTW)
    - Similitud por Coseno
"""
from .euclidean import euclidean_distance, euclidean_distance_normalized, euclidean_similarity_score
from .pearson import pearson_correlation, interpret_correlation
from .dtw import dynamic_time_warping, dynamic_time_warping_normalized, get_dtw_path, dtw_similarity_score
from .cosine import cosine_similarity, cosine_angle, interpret_cosine_similarity

SIMILARITY_ALGORITHMS = {
    'Distancia Euclidiana': {
        'func': euclidean_similarity_score,
        'tipo': 'distancia',
    },
    'Correlacion de Pearson': {
        'func': pearson_correlation,
        'tipo': 'correlacion',
    },
    'Dynamic Time Warping': {
        'func': dtw_similarity_score,
        'tipo': 'distancia',
    },
    'Similitud por Coseno': {
        'func': cosine_similarity,
        'tipo': 'similitud',
    },
}

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.requerimiento_2.algoritmos_similitud.similitud import correlacion_pearson

def generar_matriz_correlacion(df, columna="Close"):
    tickers = sorted(df["Ticker"].unique())
    matriz = pd.DataFrame(index=tickers, columns=tickers, dtype=float)
    for t1 in tickers:
        for t2 in tickers:
            if t1 == t2:
                matriz.loc[t1, t2] = 1.0
            else:
                s1 = df[df["Ticker"] == t1].sort_values("Date")[columna].values
                s2 = df[df["Ticker"] == t2].sort_values("Date")[columna].values
                r1 = np.diff(s1) / s1[:-1]
                r2 = np.diff(s2) / s2[:-1]
                min_len = min(len(r1), len(r2))
                r1, r2 = r1[:min_len], r2[:min_len]
                r1 = r1[np.isfinite(r1)]
                r2 = r2[np.isfinite(r2)]
                if len(r1) > 1 and len(r2) > 1:
                    matriz.loc[t1, t2] = correlacion_pearson(r1, r2)
                else:
                    matriz.loc[t1, t2] = 0.0
    return matriz.astype(float)

def graficar_mapa_calor(matriz_correlacion, titulo="Matriz de Correlacion - Retornos Diarios", guardar=True, ruta=None):
    if ruta is None:
        from pathlib import Path
        ruta = Path(__file__).resolve().parents[3] / "reports" / "mapa_calor_correlacion.png"
        ruta.parent.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        matriz_correlacion.astype(float),
        annot=True, fmt=".2f", cmap="RdYlBu", center=0,
        square=True, linewidths=0.5, ax=ax,
    )
    ax.set_title(titulo, fontsize=14, fontweight="bold")
    plt.tight_layout()
    if guardar:
        plt.savefig(ruta, dpi=150, bbox_inches="tight")
        plt.close()
    return fig

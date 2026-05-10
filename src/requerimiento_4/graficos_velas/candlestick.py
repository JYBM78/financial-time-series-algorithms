import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def calcular_media_movil(precios, ventana=20):
    if len(precios) < ventana:
        return np.full(len(precios), np.nan)
    serie = pd.Series(precios)
    return serie.rolling(window=ventana, min_periods=1).mean().values

def graficar_candlestick(df, ticker, ventanas_medias=(20, 50), guardar=True, ruta=None):
    sub = df[df["Ticker"] == ticker].sort_values("Date").copy()
    if len(sub) < 10:
        return None
    if ruta is None:
        from pathlib import Path
        ruta = Path(__file__).resolve().parents[3] / "reports" / f"candlestick_{ticker}.png"
        ruta.parent.mkdir(exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    fechas = sub["Date"].values
    opens = sub["Open"].values
    highs = sub["High"].values
    lows = sub["Low"].values
    closes = sub["Close"].values
    volumes = sub["Volume"].values
    fechas_num = mdates.date2num(pd.to_datetime(fechas))
    width = max(0.3, (fechas_num[-1] - fechas_num[0]) / len(fechas) * 0.6)
    for i in range(len(sub)):
        color = "green" if closes[i] >= opens[i] else "red"
        ax1.plot([fechas_num[i], fechas_num[i]], [lows[i], highs[i]], color=color, linewidth=1)
        ax1.plot([fechas_num[i] - width / 2, fechas_num[i] + width / 2],
                 [opens[i], opens[i]], color=color, linewidth=2)
        ax1.plot([fechas_num[i] - width / 2, fechas_num[i] + width / 2],
                 [closes[i], closes[i]], color=color, linewidth=2)
    for v in ventanas_medias:
        mm = calcular_media_movil(closes, v)
        ax1.plot(fechas_num, mm, label=f"MM {v}d", linewidth=1.5, alpha=0.8)
    ax1.set_ylabel("Precio")
    ax1.set_title(f"Grafico de Velas - {ticker}", fontsize=14, fontweight="bold")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax2.bar(fechas_num, volumes, color="steelblue", alpha=0.6, width=width)
    ax2.set_ylabel("Volumen")
    ax2.set_xlabel("Fecha")
    ax2.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    if guardar:
        plt.savefig(ruta, dpi=150, bbox_inches="tight")
        plt.close()
    return fig

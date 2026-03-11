"""Probe helper para intentar variantes de tickers fallidos.

Lee `data/failures.txt` (formato: TICKER;RAZON) y para cada ticker genera variantes
simples (sin sufijo, reemplazos de '.'), consulta el endpoint de Yahoo y guarda el
primer resultado válido encontrado en `data/raw`.

Genera además `data/failures_probe_results.csv` con las variantes probadas y el estado.
"""
from __future__ import annotations
import os
import time
import random
import requests
import datetime as dt
import pandas as pd
from typing import List, Tuple


def generate_variants(ticker: str) -> List[str]:
    """Genera un conjunto pequeño de variantes a probar para un ticker dado."""
    variants = []
    ticker = ticker.strip()
    variants.append(ticker)

    # si contiene '.', añadir la parte antes del punto
    if '.' in ticker:
        base = ticker.split('.')[0]
        variants.append(base)
        variants.append(base + ticker[ticker.find('.'):])  # same as original
        variants.append(base.replace('.', '') )

    # reemplazos comunes
    variants.append(ticker.replace('.', '-'))
    variants.append(ticker.replace('.', ''))

    # añadir lower/upper
    more = []
    for v in variants:
        more.append(v.upper())
        more.append(v.lower())

    variants.extend(more)

    # dedup while preserving order
    seen = set()
    out = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def probe_variant(ticker_variant: str, fecha_inicio: dt.datetime, fecha_fin: dt.datetime) -> Tuple[bool, str, pd.DataFrame]:
    """Consulta el endpoint Yahoo para el ticker_variant. Devuelve (ok, razon, df).
    ok=True y df no vacío cuando se encuentra un resultado válido.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_variant}"
    params = {
        'period1': int(fecha_inicio.timestamp()),
        'period2': int(fecha_fin.timestamp()),
        'interval': '1d'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }

    try:
        # ligero jitter
        time.sleep(random.uniform(0.5, 1.5))
        r = requests.get(url, params=params, headers=headers, timeout=10)
    except Exception as e:
        return False, f'request_error: {e}', pd.DataFrame()

    if r.status_code != 200:
        return False, f'HTTP_{r.status_code}', pd.DataFrame()

    try:
        data = r.json()
    except Exception as e:
        return False, f'json_error: {e}', pd.DataFrame()

    if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        return False, 'no_result', pd.DataFrame()

    result = data['chart']['result'][0]
    if 'timestamp' not in result or 'indicators' not in result:
        return False, 'missing_fields', pd.DataFrame()

    timestamps = result['timestamp']
    precios = result['indicators']['quote'][0]

    df = pd.DataFrame({
        'Date': pd.to_datetime(timestamps, unit='s'),
        'Open': precios.get('open', [None] * len(timestamps)),
        'High': precios.get('high', [None] * len(timestamps)),
        'Low': precios.get('low', [None] * len(timestamps)),
        'Close': precios.get('close', [None] * len(timestamps)),
        'Volume': precios.get('volume', [None] * len(timestamps))
    }).set_index('Date')

    if df.empty:
        return False, 'empty_df', df

    return True, 'ok', df


def probe_ticker(ticker: str, fecha_inicio: dt.datetime, fecha_fin: dt.datetime, carpeta: str = 'data/raw') -> List[Tuple[str, str, str]]:
    """Intenta variantes y guarda el primer CSV válido. Devuelve lista de (variant, status, path_or_reason)."""
    variants = generate_variants(ticker)
    results = []
    os.makedirs(carpeta, exist_ok=True)

    for v in variants:
        ok, reason, df = probe_variant(v, fecha_inicio, fecha_fin)
        if ok:
            # guardar CSV con nombre que indique la variante usada
            ticker_limpio = v.replace('.', '_')
            nombre = f"{ticker_limpio}_{fecha_inicio.date()}_{fecha_fin.date()}.csv"
            path = os.path.join(carpeta, nombre)
            df.to_csv(path, sep=';', encoding='utf-8-sig')
            results.append((v, 'found', path))
            # dejar de probar variantes
            return results
        else:
            results.append((v, reason, ''))

    return results


def main():
    failures_path = os.path.join('data', 'failures.txt')
    if not os.path.exists(failures_path):
        print('No se encontró data/failures.txt; no hay tickers para probar.')
        return

    # mismo rango que descargar_todos
    fecha_fin = dt.datetime.today()
    fecha_inicio = fecha_fin - dt.timedelta(days=5*365)

    lines = open(failures_path, 'r', encoding='utf-8').read().strip().splitlines()
    probe_rows = []

    for line in lines:
        if not line.strip():
            continue
        parts = line.split(';')
        ticker = parts[0].strip()
        print(f'Probando variantes para {ticker}...')
        res = probe_ticker(ticker, fecha_inicio, fecha_fin, carpeta='data/raw')
        for variant, status, path in res:
            probe_rows.append({'ticker': ticker, 'variant': variant, 'status': status, 'path': path})

    # guardar resultados
    df_res = pd.DataFrame(probe_rows)
    os.makedirs('data', exist_ok=True)
    out = os.path.join('data', 'failures_probe_results.csv')
    df_res.to_csv(out, index=False, sep=';')
    print(f'Resultados guardados en {out}')


if __name__ == '__main__':
    main()

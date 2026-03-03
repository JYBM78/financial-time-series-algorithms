from .config import TICKERS_COL
import datetime as dt
import requests
import pandas as pd
import time
import random
import os

def descargar_historico(ticker, fecha_inicio, fecha_fin, guardar=True, carpeta="datos_historicos"):
    """
    Descarga datos históricos de Yahoo Finance con manejo de rate limiting

    Parámetros:
    - ticker: Código del activo (ej: "ISA.CL")
    - fecha_inicio: datetime con fecha inicial
    - fecha_fin: datetime con fecha final
    - guardar: Si True, guarda automáticamente el CSV
    - carpeta: Carpeta donde guardar los archivos
    """
    # Convertir fechas a timestamp UNIX
    period1 = int(fecha_inicio.timestamp())
    period2 = int(fecha_fin.timestamp())

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d"
    }

    # Headers para simular un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://finance.yahoo.com/'
    }

    # Agregar delay aleatorio antes de la petición
    time.sleep(random.uniform(1, 3))

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        # Manejo de errores HTTP
        if response.status_code == 429:
            print(f"Rate limit alcanzado. Esperando 60 segundos...")
            time.sleep(60)
            # Reintentar una vez
            response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return pd.DataFrame()

        data = response.json()

    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Response text: {response.text[:500]}")
        return pd.DataFrame()
    except requests.exceptions.Timeout:
        print(f"Request timeout for {ticker}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return pd.DataFrame()

    # Validar estructura de respuesta
    if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        print(f"Error: Unexpected API response structure for ticker {ticker}")
        return pd.DataFrame()

    result = data['chart']['result'][0]

    # Validar que existan datos
    if 'timestamp' not in result or 'indicators' not in result:
        print(f"Error: Missing data in response for {ticker}")
        return pd.DataFrame()

    timestamps = result['timestamp']
    precios = result['indicators']['quote'][0]

    # Crear DataFrame
    df = pd.DataFrame({
        'Date': pd.to_datetime(timestamps, unit='s'),
        'Open': precios.get('open', [None] * len(timestamps)),
        'High': precios.get('high', [None] * len(timestamps)),
        'Low': precios.get('low', [None] * len(timestamps)),
        'Close': precios.get('close', [None] * len(timestamps)),
        'Volume': precios.get('volume', [None] * len(timestamps))
    })

    df = df.set_index('Date')

    print(f"Descargados {len(df)} registros para {ticker}")

    # ========== GUARDAR AUTOMÁTICAMENTE SI SE SOLICITA ==========
    if guardar and not df.empty:
        # Crear carpeta si no existe
        os.makedirs(carpeta, exist_ok=True)

        # Nombre del archivo
        ticker_limpio = ticker.replace('.', '_')
        nombre_archivo = f"{ticker_limpio}_{fecha_inicio.date()}_{fecha_fin.date()}.csv"
        ruta_completa = os.path.join(carpeta, nombre_archivo)

        # Guardar con punto y coma como separador
        df.to_csv(ruta_completa, sep=';', encoding='utf-8-sig')

        print(f"Guardado en: {ruta_completa}")
        print(f"Ubicación completa: {os.path.abspath(ruta_completa)}")
    # ============================================================

    return df


def descargar_todos():

    fecha_fin = dt.datetime.today()
    fecha_inicio = fecha_fin - dt.timedelta(days=5*365)

    for ticker in TICKERS_COL:

        print(f"Descargando {ticker}...")

        descargar_historico(
            ticker,
            fecha_inicio,
            fecha_fin,
            guardar=True,
            carpeta="data/raw"
        )
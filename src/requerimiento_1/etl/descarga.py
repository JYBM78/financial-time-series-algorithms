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

    # Reintentos con exponential backoff y jitter
    # Sleep inicial antes de la primera petición para mitigar rate limiting
    time.sleep(random.uniform(1, 3))

    max_retries = 3
    backoff_base = 2
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)

            # Manejo de errores HTTP
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError as e:
                    last_error = f"JSON decode error: {e}"
                    # no retry for invalid JSON
                    break
                else:
                    # éxito
                    break

            # Si es 404 -> no existe el ticker (fallo definitivo)
            if response.status_code == 404:
                last_error = f"404 Not Found"
                data = None
                break

            # Si es rate limit, reintentar con backoff
            if response.status_code == 429:
                last_error = f"429 Rate limit"
                sleep_time = backoff_base ** attempt + random.uniform(0, 1)
                print(f"Rate limit alcanzado para {ticker}. Esperando {sleep_time:.1f}s antes de reintentar (intento {attempt})")
                time.sleep(sleep_time)
                continue

            # Otros códigos de error -> intentar reintentar
            last_error = f"HTTP {response.status_code}"
            sleep_time = backoff_base ** attempt + random.uniform(0, 1)
            print(f"HTTP {response.status_code} para {ticker}. Reintentando en {sleep_time:.1f}s (intento {attempt})")
            time.sleep(sleep_time)
            continue

        except requests.exceptions.Timeout:
            last_error = "timeout"
            sleep_time = backoff_base ** attempt + random.uniform(0, 1)
            print(f"Timeout para {ticker}. Reintentando en {sleep_time:.1f}s (intento {attempt})")
            time.sleep(sleep_time)
            continue
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            sleep_time = backoff_base ** attempt + random.uniform(0, 1)
            print(f"Request error para {ticker}: {e}. Reintentando en {sleep_time:.1f}s (intento {attempt})")
            time.sleep(sleep_time)
            continue

    else:
        # Si agotamos los reintentos
        print(f"Error: No se pudo descargar {ticker} después de {max_retries} intentos. Último error: {last_error}")
        return pd.DataFrame(), last_error

    # Si aquí data es None o no trae estructura válida
    if data is None or 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
        reason = last_error or 'Unexpected API response structure'
        print(f"Error: Unexpected API response structure for ticker {ticker}: {reason}")
        return pd.DataFrame(), reason

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

    return df, None


def descargar_todos():

    fecha_fin = dt.datetime.today()
    fecha_inicio = fecha_fin - dt.timedelta(days=5*365)
    failed = []

    for ticker in TICKERS_COL:
        print(f"Descargando {ticker}...")

        df, error = descargar_historico(
            ticker,
            fecha_inicio,
            fecha_fin,
            guardar=True,
            carpeta="data/raw"
        )

        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            # Registrar fallo
            reason = error or 'empty dataframe'
            failed.append((ticker, reason))

    # Guardar reporte de fallos
    if failed:
        os.makedirs('data', exist_ok=True)
        fail_path = os.path.join('data', 'failures.txt')
        with open(fail_path, 'w', encoding='utf-8') as f:
            for t, r in failed:
                f.write(f"{t};{r}\n")
        print(f"Se registraron fallos en la descarga. Ver {fail_path}")
    else:
        # eliminar archivo de fallos si existía
        try:
            os.remove(os.path.join('data', 'failures.txt'))
        except OSError:
            pass
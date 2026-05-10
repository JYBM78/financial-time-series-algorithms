#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.requerimiento_1.etl.descarga import descargar_todos
from src.requerimiento_1.etl.unificacion import unificar

def main():
    print("=" * 60)
    print("FINANCIAL TIME SERIES ALGORITHMS")
    print("=" * 60)

    print("\nETAPA 1: DESCARGA")
    descargar_todos()

    print("\nETAPA 2: UNIFICACION")
    df = unificar()

    print(f"\nDatos unificados: {len(df)} registros de {df['Ticker'].nunique()} activos")
    print(df.head())

if __name__ == "__main__":
    main()

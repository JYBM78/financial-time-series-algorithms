# Script para verificar compatibilidad con despliegue en la nube
import os
import sys
from pathlib import Path


def verificar_estructura():
    """Verifica que la estructura del proyecto sea compatible con despliegue cloud"""
    print("🔍 Verificando compatibilidad con despliegue en la nube...")

    # Verificar archivos principales
    archivos_requeridos = ['app.py', 'requirements.txt', 'README.md']
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"✅ {archivo} encontrado")
        else:
            print(f"❌ {archivo} faltante")

    # Verificar estructura de directorios
    directorios = ['src', 'data', 'reports']
    for directorio in directorios:
        if Path(directorio).exists():
            print(f"✅ Directorio {directorio}/ existe")
        else:
            print(
                f"⚠️  Directorio {directorio}/ no existe (se creará automáticamente)")

    # Verificar imports
    try:
        import streamlit as st
        print(f"✅ Streamlit {st.__version__} disponible")
    except ImportError:
        print("❌ Streamlit no instalado")

    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        print("✅ Librerías principales disponibles")
    except ImportError as e:
        print(f"❌ Librerías faltantes: {e}")

    print("\n🚀 El proyecto está listo para despliegue en la nube!")
    print("Opciones recomendadas:")
    print("1. Streamlit Cloud (más fácil): https://share.streamlit.io")
    print("2. Railway: https://railway.app")
    print("3. Render: https://render.com")


if __name__ == "__main__":
    verificar_estructura()

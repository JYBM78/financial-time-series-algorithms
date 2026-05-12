from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

APP_ROOT = PROJECT_ROOT / "src" / "requerimiento_5"

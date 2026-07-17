import sqlite3
from pathlib import Path

# Ruta absoluta a la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_BD = BASE_DIR / "database" / "asistencia.db"

def conectar():

    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    return conexion
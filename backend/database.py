import sqlite3
from pathlib import Path

# Ruta absoluta a la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_BD = BASE_DIR / "database" / "asistencia.db"

def conectar():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row

    # Verificar columnas existentes
    columnas = [
        fila["name"]
        for fila in conexion.execute("PRAGMA table_info(alumnos)")
    ]

    # Agregar columna faltante sin eliminar registros
    if columnas and "rostro_registrado" not in columnas:
        conexion.execute(
            "ALTER TABLE alumnos "
            "ADD COLUMN rostro_registrado INTEGER DEFAULT 0"
        )
        conexion.commit()

    return conexion
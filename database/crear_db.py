import sqlite3

conexion = sqlite3.connect(
    "database/asistencia.db"
)

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno TEXT,
    fecha TEXT,
    hora TEXT
)
""")

conexion.commit()

conexion.close()

print("Base de datos creada correctamente")
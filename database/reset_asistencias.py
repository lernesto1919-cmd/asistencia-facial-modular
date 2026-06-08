import sqlite3

conexion = sqlite3.connect("database/asistencia.db")
cursor = conexion.cursor()

cursor.execute("DROP TABLE IF EXISTS asistencias")

cursor.execute("""
CREATE TABLE asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER,
    fecha TEXT,
    hora TEXT,
    FOREIGN KEY(alumno_id) REFERENCES alumnos(id)
)
""")

conexion.commit()
conexion.close()

print("Tabla asistencias reiniciada correctamente")
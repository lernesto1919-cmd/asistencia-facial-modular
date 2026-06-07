from backend.database import conectar

def crear_tabla_asistencias():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            fecha TEXT,
            hora TEXT,
            FOREIGN KEY(alumno_id) REFERENCES alumnos(id)
        )
    """)

    conexion.commit()
    conexion.close()
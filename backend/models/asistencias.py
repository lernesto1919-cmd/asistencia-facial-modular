from backend.database import conectar

def crear_tabla_asistencias():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            grupo_id INTEGER,
            fecha TEXT,
            hora TEXT,
            FOREIGN KEY(alumno_id) REFERENCES alumnos(id),
            FOREIGN KEY(grupo_id) REFERENCES grupos(id)
        )
    """)

    # Agregar grupo_id a bases de datos que ya existían
    try:
        cursor.execute("""
            ALTER TABLE asistencias
            ADD COLUMN grupo_id INTEGER
        """)
    except:
        pass

    conexion.commit()
    conexion.close()
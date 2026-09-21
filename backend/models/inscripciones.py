from backend.database import conectar


def crear_tabla_inscripciones():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            grupo_id INTEGER NOT NULL,

            FOREIGN KEY (alumno_id)
            REFERENCES alumnos(id),

            FOREIGN KEY (grupo_id)
            REFERENCES grupos(id),

            UNIQUE(alumno_id, grupo_id)
        )
    """)

    conexion.commit()
    conexion.close()
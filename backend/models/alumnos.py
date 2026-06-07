from backend.database import conectar

def crear_tabla_alumnos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            matricula TEXT NOT NULL,
            grupo TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()
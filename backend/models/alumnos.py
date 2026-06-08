from backend.database import conectar

def crear_tabla_alumnos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            matricula TEXT NOT NULL,
            grupo TEXT,
            grupo_id INTEGER,
            FOREIGN KEY(grupo_id) REFERENCES grupos(id)
        )
    """)

    try:
        cursor.execute("ALTER TABLE alumnos ADD COLUMN grupo_id INTEGER")
    except:
        pass

    conexion.commit()
    conexion.close()
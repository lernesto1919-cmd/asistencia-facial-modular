from backend.database import conectar

def crear_tabla_grupos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            maestro_id INTEGER,
            FOREIGN KEY(maestro_id) REFERENCES maestros(id)
        )
    """)

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN maestro_id INTEGER")
    except:
        pass

    conexion.commit()
    conexion.close()
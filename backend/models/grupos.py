from backend.database import conectar

def crear_tabla_grupos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            aula TEXT,
            hora_clase TEXT,
            maestro_id INTEGER,
            FOREIGN KEY(maestro_id) REFERENCES maestros(id)
        )
    """)

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN maestro_id INTEGER")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN aula TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN hora_clase TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN materia TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN hora_inicio TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN hora_fin TEXT")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN dias TEXT")
    except:
        pass

    conexion.commit()
    conexion.close()
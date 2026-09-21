from backend.database import conectar
import secrets
import string


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

    try:
        cursor.execute("ALTER TABLE grupos ADD COLUMN codigo TEXT")
    except:
        pass

    # Dar código a los grupos que ya existían
    cursor.execute("""
        SELECT id
        FROM grupos
        WHERE codigo IS NULL OR codigo = ''
    """)

    grupos_sin_codigo = cursor.fetchall()

    for grupo in grupos_sin_codigo:

        while True:
            caracteres = string.ascii_uppercase + string.digits

            codigo = "".join(
                secrets.choice(caracteres)
                for _ in range(6)
            )

            cursor.execute("""
                SELECT id
                FROM grupos
                WHERE codigo = ?
            """, (codigo,))

            if not cursor.fetchone():
                break

        cursor.execute("""
            UPDATE grupos
            SET codigo = ?
            WHERE id = ?
        """, (
            codigo,
            grupo["id"]
        ))

    conexion.commit()
    conexion.close()
from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/maestros")
def crear_maestro(data: dict):

    nombre = str(data.get("nombre", "")).strip()
    correo = str(data.get("correo", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    # Validar campos vacíos
    if not nombre or not correo or not password:
        return {
            "ok": False,
            "mensaje": "Todos los campos son obligatorios"
        }

    # Validación básica del correo
    if "@" not in correo or "." not in correo:
        return {
            "ok": False,
            "mensaje": "Ingresa un correo válido"
        }

    # Validar longitud de contraseña
    if len(password) < 6:
        return {
            "ok": False,
            "mensaje": "La contraseña debe tener al menos 6 caracteres"
        }

    conexion = conectar()
    cursor = conexion.cursor()

    # Revisar si el correo ya existe
    cursor.execute("""
        SELECT id
        FROM maestros
        WHERE correo = ?
    """, (correo,))

    maestro_existente = cursor.fetchone()

    if maestro_existente:
        conexion.close()

        return {
            "ok": False,
            "mensaje": "Ya existe una cuenta con este correo"
        }

    # Crear maestro
    cursor.execute("""
        INSERT INTO maestros (nombre, correo, password)
        VALUES (?, ?, ?)
    """, (
        nombre,
        correo,
        password
    ))

    conexion.commit()

    maestro_id = cursor.lastrowid

    conexion.close()

    return {
        "ok": True,
        "mensaje": "Cuenta creada correctamente",
        "maestro": {
            "id": maestro_id,
            "nombre": nombre,
            "correo": correo
        }
    }


@router.post("/login")
def login(data: dict):

    correo = str(data.get("correo", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not correo or not password:
        return {
            "acceso": False,
            "mensaje": "Correo y contraseña son obligatorios"
        }

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, correo
        FROM maestros
        WHERE LOWER(correo) = ?
        AND password = ?
    """, (
        correo,
        password
    ))

    maestro = cursor.fetchone()
    conexion.close()

    if maestro:
        return {
            "acceso": True,
            "maestro": dict(maestro)
        }

    return {
        "acceso": False,
        "mensaje": "Credenciales incorrectas"
    }
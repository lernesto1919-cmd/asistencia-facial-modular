from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/maestros")
def crear_maestro(data: dict):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO maestros (nombre, correo, password)
        VALUES (?, ?, ?)
    """, (
        data["nombre"],
        data["correo"],
        data["password"]
    ))

    conexion.commit()
    conexion.close()

    return {
        "mensaje": "Maestro creado"
    }


@router.post("/login")
def login(data: dict):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, correo
        FROM maestros
        WHERE correo = ?
        AND password = ?
    """, (
        data["correo"],
        data["password"]
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
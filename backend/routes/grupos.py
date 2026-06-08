from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/grupos")
def crear_grupo(data: dict):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO grupos (nombre, descripcion)
        VALUES (?, ?)
    """, (
        data["nombre"],
        data.get("descripcion", "")
    ))

    conexion.commit()
    conexion.close()

    return {
        "mensaje": "Grupo creado"
    }


@router.get("/grupos")
def obtener_grupos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM grupos")
    grupos = cursor.fetchall()

    conexion.close()

    return [dict(grupo) for grupo in grupos]
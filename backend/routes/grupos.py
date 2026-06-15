from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/grupos")
def crear_grupo(data: dict):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO grupos (
            nombre,
            descripcion,
            materia,
            aula,
            dias,
            hora_inicio,
            hora_fin,
            maestro_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["nombre"],
        data.get("descripcion", ""),
        data.get("materia", ""),
        data.get("aula", ""),
        data["dias"],
        data.get("hora_inicio", ""),
        data.get("hora_fin", ""),
        data["maestro_id"]
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


@router.get("/maestros/{maestro_id}/grupos")
def obtener_grupos_por_maestro(maestro_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM grupos
        WHERE maestro_id = ?
    """, (maestro_id,))

    grupos = cursor.fetchall()

    conexion.close()

    return [dict(grupo) for grupo in grupos]
from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/alumnos")
def crear_alumno(data: dict):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO alumnos (nombre, matricula, grupo, grupo_id)
        VALUES (?, ?, ?, ?)
    """, (
        data["nombre"],
        data["matricula"],
        data.get("grupo", ""),
        data.get("grupo_id")
    ))

    conexion.commit()
    conexion.close()

    return {"mensaje": "Alumno creado"}


@router.get("/alumnos")
def obtener_alumnos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT 
            alumnos.id,
            alumnos.nombre,
            alumnos.matricula,
            alumnos.grupo,
            alumnos.grupo_id,
            grupos.nombre AS nombre_grupo
        FROM alumnos
        LEFT JOIN grupos
        ON alumnos.grupo_id = grupos.id
    """)

    alumnos = cursor.fetchall()
    conexion.close()

    return [dict(alumno) for alumno in alumnos]


@router.get("/grupos/{grupo_id}/alumnos")
def obtener_alumnos_por_grupo(grupo_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM alumnos
        WHERE grupo_id = ?
    """, (grupo_id,))

    alumnos = cursor.fetchall()
    conexion.close()

    return [dict(alumno) for alumno in alumnos]
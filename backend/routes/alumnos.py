from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/alumnos")
def crear_alumno(data: dict):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO alumnos (nombre, matricula, grupo)
        VALUES (?, ?, ?)
    """, (
        data["nombre"],
        data["matricula"],
        data["grupo"]
    ))

    conexion.commit()
    conexion.close()

    return {"mensaje": "Alumno creado"}


@router.get("/alumnos")
def obtener_alumnos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM alumnos")
    alumnos = cursor.fetchall()

    conexion.close()

    return [dict(alumno) for alumno in alumnos]
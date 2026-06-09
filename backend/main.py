from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from backend.routes import grupos
from backend.models.grupos import crear_tabla_grupos
from backend.routes import asistencia_activa

from backend.database import conectar
from backend.routes import alumnos
from backend.models.alumnos import crear_tabla_alumnos
from backend.models.asistencias import crear_tabla_asistencias

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crear_tabla_alumnos()
crear_tabla_asistencias()
crear_tabla_grupos()

app.include_router(alumnos.router)
app.include_router(grupos.router)
app.include_router(asistencia_activa.router)

class Asistencia(BaseModel):
    alumno: str


@app.get("/")
def inicio():
    return {
        "mensaje": "Sistema de asistencia facial funcionando"
    }


@app.post("/registrar")
def registrar_asistencia(data: Asistencia):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id FROM alumnos
        WHERE nombre = ?
    """, (data.alumno,))

    alumno = cursor.fetchone()

    if not alumno:
        conexion.close()
        return {
            "error": "Alumno no encontrado"
        }

    alumno_id = alumno["id"]

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    cursor.execute("""
        INSERT INTO asistencias (alumno_id, fecha, hora)
        VALUES (?, ?, ?)
    """, (
        alumno_id,
        fecha,
        hora
    ))

    conexion.commit()
    conexion.close()

    return {
        "mensaje": "Asistencia registrada"
    }


@app.get("/asistencias")
def obtener_asistencias():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            asistencias.id,
            alumnos.nombre,
            asistencias.fecha,
            asistencias.hora
        FROM asistencias
        INNER JOIN alumnos
        ON asistencias.alumno_id = alumnos.id
    """)

    asistencias = cursor.fetchall()
    conexion.close()

    return [dict(asistencia) for asistencia in asistencias]


@app.get("/estadisticas")
def estadisticas():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) as total_alumnos FROM alumnos")
    total_alumnos = cursor.fetchone()["total_alumnos"]

    cursor.execute("SELECT COUNT(*) as total_asistencias FROM asistencias")
    total_asistencias = cursor.fetchone()["total_asistencias"]

    conexion.close()

    return {
        "total_alumnos": total_alumnos,
        "total_asistencias": total_asistencias
    }

@app.get("/grupos/{grupo_id}/asistencias")
def obtener_asistencias_por_grupo(grupo_id: int):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            asistencias.id,
            alumnos.nombre,
            alumnos.matricula,
            alumnos.grupo_id,
            asistencias.fecha,
            asistencias.hora
        FROM asistencias
        INNER JOIN alumnos
        ON asistencias.alumno_id = alumnos.id
        WHERE alumnos.grupo_id = ?
    """, (grupo_id,))

    asistencias = cursor.fetchall()

    conexion.close()

    return [
        dict(asistencia)
        for asistencia in asistencias
    ]
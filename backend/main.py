from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from backend.routes import grupos
from backend.models.grupos import crear_tabla_grupos
from backend.routes import asistencia_activa
from backend.routes.asistencia_activa import grupo_activo

from backend.database import conectar
from backend.routes import alumnos
from backend.models.alumnos import crear_tabla_alumnos
from backend.models.asistencias import crear_tabla_asistencias

from backend.routes import maestros
from backend.models.maestros import crear_tabla_maestros

from backend.models.inscripciones import crear_tabla_inscripciones

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
crear_tabla_maestros()
crear_tabla_inscripciones()

app.include_router(alumnos.router)
app.include_router(grupos.router)
app.include_router(asistencia_activa.router)
app.include_router(maestros.router)

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

    # Buscar alumno
    cursor.execute("""
        SELECT id
        FROM alumnos
        WHERE nombre = ?
    """, (data.alumno,))

    alumno = cursor.fetchone()

    if not alumno:
        conexion.close()
        return {
            "error": "Alumno no encontrado"
        }

    alumno_id = alumno["id"]

    # Obtener grupo activo
    grupo_id = grupo_activo["grupo_id"]

    if grupo_id is None:
        conexion.close()
        return {
            "error": "No hay un grupo activo"
    }

    # Verificar que el alumno esté inscrito en la clase activa
    cursor.execute("""
        SELECT id
        FROM inscripciones
        WHERE alumno_id = ?
        AND grupo_id = ?
    """, (
        alumno_id,
        grupo_id
    ))

    inscripcion = cursor.fetchone()

    if not inscripcion:
        conexion.close()
        return {
            "error": "El alumno no pertenece al grupo activo"
        }

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    # Evitar duplicado dentro de la misma clase
    cursor.execute("""
        SELECT id
        FROM asistencias
        WHERE alumno_id = ?
        AND grupo_id = ?
        AND fecha = ?
    """, (
        alumno_id,
        grupo_id,
        fecha
    ))

    asistencia_existente = cursor.fetchone()

    if asistencia_existente:
        conexion.close()
        return {
            "mensaje": "La asistencia ya estaba registrada",
            "alumno": data.alumno,
            "grupo_id": grupo_id,
            "fecha": fecha
        }

    # Registrar asistencia
    cursor.execute("""
        INSERT INTO asistencias (
            alumno_id,
            grupo_id,
            fecha,
            hora
        )
        VALUES (?, ?, ?, ?)
    """, (
        alumno_id,
        grupo_id,
        fecha,
        hora
    ))

    conexion.commit()
    conexion.close()

    return {
        "mensaje": "Asistencia registrada",
        "alumno": data.alumno,
        "grupo_id": grupo_id,
        "fecha": fecha,
        "hora": hora
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

@app.get("/maestros/{maestro_id}/asistencias")
def obtener_asistencias_por_maestro(maestro_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            asistencias.id,
            alumnos.nombre,
            alumnos.matricula,
            asistencias.grupo_id,
            grupos.nombre AS nombre_grupo,
            grupos.materia,
            asistencias.fecha,
            asistencias.hora
        FROM asistencias

        INNER JOIN alumnos
        ON asistencias.alumno_id = alumnos.id

        INNER JOIN grupos
        ON asistencias.grupo_id = grupos.id

        WHERE grupos.maestro_id = ?

        ORDER BY
            asistencias.fecha DESC,
            asistencias.hora DESC
    """, (maestro_id,))

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

@app.get("/maestros/{maestro_id}/estadisticas")
def estadisticas_por_maestro(maestro_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    # Contar alumnos únicos inscritos en grupos del maestro
    cursor.execute("""
        SELECT COUNT(DISTINCT inscripciones.alumno_id) AS total_alumnos
        FROM inscripciones

        INNER JOIN grupos
        ON inscripciones.grupo_id = grupos.id

        WHERE grupos.maestro_id = ?
    """, (maestro_id,))

    total_alumnos = cursor.fetchone()["total_alumnos"]

    # Contar asistencias registradas en grupos del maestro
    cursor.execute("""
        SELECT COUNT(*) AS total_asistencias
        FROM asistencias

        INNER JOIN grupos
        ON asistencias.grupo_id = grupos.id

        WHERE grupos.maestro_id = ?
    """, (maestro_id,))

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
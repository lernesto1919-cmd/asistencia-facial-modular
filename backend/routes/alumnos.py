from fastapi import APIRouter
from backend.database import conectar

import subprocess
import sys
import os
import shutil

router = APIRouter()

@router.post("/alumnos")
def crear_alumno(data: dict):

    nombre = str(data.get("nombre", "")).strip()
    matricula = str(data.get("matricula", "")).strip()
    grupo = str(data.get("grupo", "")).strip()
    grupo_id = data.get("grupo_id")

    # Validar campos obligatorios
    if not nombre or not matricula or not grupo:
        return {
            "ok": False,
            "mensaje": "Nombre, matrícula y grupo son obligatorios"
        }

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO alumnos (nombre, matricula, grupo, grupo_id)
        VALUES (?, ?, ?, ?)
    """, (
        nombre,
        matricula,
        grupo,
        grupo_id
    ))

    conexion.commit()
    conexion.close()

    return {
        "ok": True,
        "mensaje": "Alumno creado"
    }

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
            alumnos.rostro_registrado,
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

@router.post("/alumnos/{alumno_id}/registrar-rostro")
def registrar_rostro(alumno_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre
        FROM alumnos
        WHERE id = ?
    """, (alumno_id,))

    alumno = cursor.fetchone()
    conexion.close()

    if not alumno:
        return {
            "ok": False,
            "mensaje": "Alumno no encontrado"
        }

    nombre = alumno["nombre"]

    try:

        # Capturar las 100 imágenes
        resultado_captura = subprocess.run([
            sys.executable,
            "ia/capturar_rostro.py",
            nombre
        ])

        if resultado_captura.returncode != 0:
            return {
                "ok": False,
                "mensaje": "La captura del rostro no terminó correctamente"
            }

        # Entrenar el modelo automáticamente
        resultado_entrenamiento = subprocess.run([
            sys.executable,
            "ia/entrenar_modelo.py"
        ])

        if resultado_entrenamiento.returncode != 0:
            return {
                "ok": False,
                "mensaje": "Las imágenes se capturaron, pero el modelo no pudo entrenarse"
            }

        if resultado_entrenamiento.returncode != 0:
            return {
                "ok": False,
                "mensaje": "Las imágenes se capturaron, pero el modelo no pudo entrenarse"
            }

        # Marcar que el alumno ya tiene rostro registrado
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE alumnos
            SET rostro_registrado = 1
            WHERE id = ?
        """, (alumno_id,))

        conexion.commit()
        conexion.close()

        return {
            "ok": True,
            "mensaje": "Rostro registrado y modelo actualizado",
            "alumno": nombre
        }

    except Exception as error:
        return {
            "ok": False,
            "mensaje": "No se pudo completar el registro facial",
            "detalle": str(error)
        }

@router.delete("/alumnos/{alumno_id}")
def eliminar_alumno(alumno_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    # Buscar alumno
    cursor.execute("""
        SELECT id, nombre
        FROM alumnos
        WHERE id = ?
    """, (alumno_id,))

    alumno = cursor.fetchone()

    if not alumno:
        conexion.close()
        return {
            "ok": False,
            "mensaje": "Alumno no encontrado"
        }

    nombre = alumno["nombre"]

    # Eliminar asistencias del alumno
    cursor.execute("""
        DELETE FROM asistencias
        WHERE alumno_id = ?
    """, (alumno_id,))

    # Eliminar alumno
    cursor.execute("""
        DELETE FROM alumnos
        WHERE id = ?
    """, (alumno_id,))

    conexion.commit()
    conexion.close()

    # Eliminar fotografías del rostro
    ruta_rostro = os.path.join(
        "ia",
        "dataset",
        nombre
    )

    if os.path.exists(ruta_rostro):
        shutil.rmtree(ruta_rostro)

    # Volver a entrenar el modelo
    try:
        subprocess.run([
            sys.executable,
            "ia/entrenar_modelo.py"
        ])
    except Exception as error:
        print(
            "No se pudo actualizar el modelo:",
            error
        )

    return {
        "ok": True,
        "mensaje": f"Alumno {nombre} eliminado"
    }
from fastapi import APIRouter
from backend.database import conectar

import subprocess
import sys
import os
import shutil
import base64

router = APIRouter()

@router.post("/alumnos")
def crear_alumno(data: dict):

    nombre = str(data.get("nombre", "")).strip()
    matricula = str(data.get("matricula", "")).strip()
    grupo = str(data.get("grupo", "")).strip()
    grupo_id = data.get("grupo_id")
    maestro_id = data.get("maestro_id")

    # Validar datos obligatorios
    if not nombre or not matricula or not grupo_id or not maestro_id:
        return {
            "ok": False,
            "mensaje": "Nombre, matrícula y grupo son obligatorios"
        }

    conexion = conectar()
    cursor = conexion.cursor()

    # Comprobar que el grupo pertenece al maestro
    cursor.execute("""
        SELECT id, nombre
        FROM grupos
        WHERE id = ?
        AND maestro_id = ?
    """, (
        grupo_id,
        maestro_id
    ))

    grupo_encontrado = cursor.fetchone()

    if not grupo_encontrado:
        conexion.close()

        return {
            "ok": False,
            "mensaje": "El grupo seleccionado no pertenece a este maestro"
        }

    # Evitar matrícula duplicada
    cursor.execute("""
        SELECT id
        FROM alumnos
        WHERE matricula = ?
    """, (matricula,))

    alumno_existente = cursor.fetchone()

    if alumno_existente:
        conexion.close()

        return {
            "ok": False,
            "mensaje": "Ya existe un alumno con esta matrícula"
        }

    # Registrar alumno
    cursor.execute("""
        INSERT INTO alumnos (
            nombre,
            matricula,
            grupo,
            grupo_id
        )
        VALUES (?, ?, ?, ?)
    """, (
        nombre,
        matricula,
        grupo_encontrado["nombre"],
        grupo_id
    ))

    # Obtener el ID del alumno recién creado
    alumno_id = cursor.lastrowid

    # Inscribir automáticamente al alumno en el grupo
    cursor.execute("""
        INSERT INTO inscripciones (
            alumno_id,
            grupo_id
        )
        VALUES (?, ?)
    """, (
        alumno_id,
        grupo_id
    ))

    conexion.commit()
    conexion.close()

    return {
        "ok": True,
        "mensaje": "Alumno registrado correctamente"
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
        SELECT
            alumnos.id,
            alumnos.nombre,
            alumnos.matricula,
            alumnos.rostro_registrado
        FROM alumnos

        INNER JOIN inscripciones
        ON alumnos.id = inscripciones.alumno_id

        WHERE inscripciones.grupo_id = ?

        ORDER BY alumnos.nombre
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

    # Verificar que existan imágenes del alumno
    carpeta = os.path.join(
        "ia",
        "dataset",
        nombre
    )

    if not os.path.exists(carpeta):
        return {
            "ok": False,
            "mensaje": "El alumno todavía no tiene imágenes registradas"
        }

    imagenes = [
        archivo
        for archivo in os.listdir(carpeta)
        if archivo.lower().endswith(".jpg")
    ]

    if len(imagenes) < 10:
        return {
            "ok": False,
            "mensaje": "No hay suficientes imágenes para entrenar el rostro"
        }

    try:
        # Entrenar el modelo con las imágenes del dataset
        resultado_entrenamiento = subprocess.run([
            sys.executable,
            "ia/entrenar_modelo.py"
        ])

        if resultado_entrenamiento.returncode != 0:
            return {
                "ok": False,
                "mensaje": "Las imágenes se guardaron, pero el modelo no pudo entrenarse"
            }

        # Marcar al alumno como rostro registrado
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
            "alumno": nombre,
            "imagenes": len(imagenes)
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

@router.get("/maestros/{maestro_id}/alumnos")
def obtener_alumnos_por_maestro(maestro_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT DISTINCT
            alumnos.id,
            alumnos.nombre,
            alumnos.matricula,
            alumnos.rostro_registrado
        FROM alumnos

        INNER JOIN inscripciones
        ON alumnos.id = inscripciones.alumno_id

        INNER JOIN grupos
        ON inscripciones.grupo_id = grupos.id

        WHERE grupos.maestro_id = ?
        ORDER BY alumnos.nombre
    """, (maestro_id,))

    alumnos = cursor.fetchall()
    conexion.close()

    return [dict(alumno) for alumno in alumnos]

@router.post("/alumnos/unirse-clase")
def unirse_clase(data: dict):

    matricula = str(data.get("matricula", "")).strip()
    codigo = str(data.get("codigo", "")).strip().upper()

    if not matricula or not codigo:
        return {
            "ok": False,
            "mensaje": "Ingresa tu matrícula y el código de la clase"
        }

    conexion = conectar()
    cursor = conexion.cursor()

    # Buscar alumno por matrícula
    cursor.execute("""
        SELECT id, nombre, matricula
        FROM alumnos
        WHERE matricula = ?
    """, (matricula,))

    alumno = cursor.fetchone()

    if not alumno:
        conexion.close()
        return {
            "ok": False,
            "mensaje": "No se encontró un alumno con esta matrícula"
        }

    # Buscar grupo por código
    cursor.execute("""
        SELECT id, nombre, materia
        FROM grupos
        WHERE UPPER(codigo) = ?
    """, (codigo,))

    grupo = cursor.fetchone()

    if not grupo:
        conexion.close()
        return {
            "ok": False,
            "mensaje": "El código de clase no es válido"
        }

    # Comprobar si ya está inscrito
    cursor.execute("""
        SELECT id
        FROM inscripciones
        WHERE alumno_id = ?
        AND grupo_id = ?
    """, (
        alumno["id"],
        grupo["id"]
    ))

    inscripcion_existente = cursor.fetchone()

    if inscripcion_existente:
        conexion.close()
        return {
            "ok": False,
            "mensaje": "Ya estás inscrito en esta clase"
        }

    # Crear inscripción
    cursor.execute("""
        INSERT INTO inscripciones (
            alumno_id,
            grupo_id
        )
        VALUES (?, ?)
    """, (
        alumno["id"],
        grupo["id"]
    ))

    conexion.commit()
    conexion.close()

    return {
        "ok": True,
        "mensaje": "Te uniste correctamente a la clase",
        "alumno": {
            "id": alumno["id"],
            "nombre": alumno["nombre"],
            "matricula": alumno["matricula"]
        },
        "grupo": {
            "id": grupo["id"],
            "nombre": grupo["nombre"],
            "materia": grupo["materia"]
        }
    }

@router.post("/alumnos/{alumno_id}/subir-rostro")
def subir_rostro(alumno_id: int, data: dict):

    imagen = data.get("imagen")

    if not imagen:
        return {
            "ok": False,
            "mensaje": "No se recibió ninguna imagen"
        }

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT nombre
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

    carpeta = os.path.join(
        "ia",
        "dataset",
        nombre
    )

    os.makedirs(carpeta, exist_ok=True)

    cantidad = len([
        archivo
        for archivo in os.listdir(carpeta)
        if archivo.lower().endswith(".jpg")
    ])

    imagen_base64 = imagen.split(",")[-1]
    imagen_bytes = base64.b64decode(imagen_base64)

    ruta_imagen = os.path.join(
        carpeta,
        f"{cantidad}.jpg"
    )

    with open(ruta_imagen, "wb") as archivo:
        archivo.write(imagen_bytes)

    return {
        "ok": True,
        "mensaje": "Imagen guardada",
        "numero": cantidad + 1
    }

@router.post("/alumnos/{alumno_id}/preparar-registro-rostro")
def preparar_registro_rostro(alumno_id: int):
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

    carpeta = os.path.join(
        "ia",
        "dataset",
        nombre
    )

    # Crear carpeta si todavía no existe
    os.makedirs(carpeta, exist_ok=True)

    # Eliminar únicamente las fotografías anteriores
    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
            ruta = os.path.join(carpeta, archivo)

            try:
                os.remove(ruta)
            except Exception as error:
                return {
                    "ok": False,
                    "mensaje": "No se pudieron limpiar las imágenes anteriores",
                    "detalle": str(error)
                }

    return {
        "ok": True,
        "mensaje": "Registro facial preparado"
    }
@router.post("/alumnos/{alumno_id}/registrar-rostro-maestro")
def registrar_rostro_maestro(alumno_id: int):
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
        # Capturar imágenes usando la cámara del equipo del maestro
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

        # Entrenar nuevamente el modelo LBPH
        resultado_entrenamiento = subprocess.run([
            sys.executable,
            "ia/entrenar_modelo.py"
        ])

        if resultado_entrenamiento.returncode != 0:
            return {
                "ok": False,
                "mensaje": "Las imágenes se capturaron, pero el modelo no pudo entrenarse"
            }

        # Marcar rostro como registrado
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
            "mensaje": "Rostro registrado correctamente desde el equipo del maestro",
            "alumno": nombre
        }

    except Exception as error:
        return {
            "ok": False,
            "mensaje": "No se pudo completar el registro facial",
            "detalle": str(error)
        }
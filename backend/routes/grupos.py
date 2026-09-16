from fastapi import APIRouter
from backend.database import conectar

router = APIRouter()

@router.post("/grupos")
def crear_grupo(data: dict):

    nombre = str(data.get("nombre", "")).strip()
    materia = str(data.get("materia", "")).strip()
    aula = str(data.get("aula", "")).strip()
    dias = data.get("dias")
    hora_inicio = str(data.get("hora_inicio", "")).strip()
    hora_fin = str(data.get("hora_fin", "")).strip()
    maestro_id = data.get("maestro_id")
    descripcion = str(data.get("descripcion", "")).strip()

    # Validar campos obligatorios
    if (
        not nombre
        or not materia
        or not aula
        or not dias
        or not hora_inicio
        or not hora_fin
        or not maestro_id
    ):
        return {
            "ok": False,
            "mensaje": "Completa todos los campos obligatorios del grupo"
        }

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
        nombre,
        descripcion,
        materia,
        aula,
        dias,
        hora_inicio,
        hora_fin,
        maestro_id
    ))

    conexion.commit()
    conexion.close()

    return {
        "ok": True,
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

@router.delete("/grupos/{grupo_id}")
def eliminar_grupo(grupo_id: int):
    conexion = conectar()
    cursor = conexion.cursor()

    # Comprobar que el grupo existe
    cursor.execute("""
        SELECT id, nombre
        FROM grupos
        WHERE id = ?
    """, (grupo_id,))

    grupo = cursor.fetchone()

    if not grupo:
        conexion.close()
        return {
            "ok": False,
            "mensaje": "Grupo no encontrado"
        }

    # Comprobar si tiene alumnos
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alumnos
        WHERE grupo_id = ?
    """, (grupo_id,))

    total_alumnos = cursor.fetchone()["total"]

    if total_alumnos > 0:
        conexion.close()

        return {
            "ok": False,
            "mensaje": f"No puedes eliminar este grupo porque tiene {total_alumnos} alumno(s) registrado(s)"
        }

    # Eliminar grupo
    cursor.execute("""
        DELETE FROM grupos
        WHERE id = ?
    """, (grupo_id,))

    conexion.commit()
    conexion.close()

    return {
        "ok": True,
        "mensaje": "Grupo eliminado"
    }
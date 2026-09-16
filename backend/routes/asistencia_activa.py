from fastapi import APIRouter
import subprocess
import sys

proceso_reconocimiento = None

router = APIRouter()

grupo_activo = {
    "grupo_id": None
}

@router.post("/iniciar-asistencia")
def iniciar_asistencia(data: dict):

    grupo_id = data.get("grupo_id")

    if not grupo_id:
        return {
            "ok": False,
            "mensaje": "Debes seleccionar un grupo"
        }

    # Guardar el grupo que actualmente está tomando asistencia
    grupo_activo["grupo_id"] = grupo_id

    try:
        # Iniciar reconocimiento facial sin bloquear FastAPI
        global proceso_reconocimiento

        proceso_reconocimiento = subprocess.Popen([
            sys.executable,
            "ia/reconocer.py"
        ])

        return {
            "ok": True,
            "mensaje": "Asistencia iniciada",
            "grupo_id": grupo_id
        }

    except Exception as error:
        grupo_activo["grupo_id"] = None

        return {
            "ok": False,
            "mensaje": "No se pudo iniciar el reconocimiento facial",
            "detalle": str(error)
        }


@router.get("/grupo-activo")
def obtener_grupo_activo():

    return grupo_activo

@router.post("/finalizar-asistencia")
def finalizar_asistencia():
    global proceso_reconocimiento

    # Desactivar el grupo
    grupo_activo["grupo_id"] = None

    # Cerrar el proceso de reconocimiento facial
    if proceso_reconocimiento is not None:
        if proceso_reconocimiento.poll() is None:
            proceso_reconocimiento.terminate()

        proceso_reconocimiento = None

    return {
        "ok": True,
        "mensaje": "Asistencia finalizada"
    }
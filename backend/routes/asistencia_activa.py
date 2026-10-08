
from fastapi import APIRouter
import subprocess
import sys

router = APIRouter()

proceso_reconocimiento = None

grupo_activo = {
    "grupo_id": None
}


@router.post("/iniciar-asistencia")
def iniciar_asistencia(data: dict):
    global proceso_reconocimiento

    grupo_id = data.get("grupo_id")
    modo = data.get("modo", "local")

    if not grupo_id:
        return {
            "ok": False,
            "mensaje": "Debes seleccionar un grupo"
        }

    if modo not in ("local", "web"):
        return {
            "ok": False,
            "mensaje": "Modo de asistencia no valido"
        }

    if grupo_activo["grupo_id"] is not None:
        return {
            "ok": False,
            "mensaje": "Ya existe una asistencia activa"
        }

    grupo_activo["grupo_id"] = grupo_id

    # Modo web: la camara se abrira desde React.
    if modo == "web":
        return {
            "ok": True,
            "mensaje": "Asistencia web iniciada",
            "grupo_id": grupo_id,
            "modo": "web"
        }

    # Modo local: conservar el funcionamiento anterior.
    try:
        proceso_reconocimiento = subprocess.Popen([
            sys.executable,
            "ia/reconocer.py"
        ])

        return {
            "ok": True,
            "mensaje": "Asistencia local iniciada",
            "grupo_id": grupo_id,
            "modo": "local"
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

    grupo_activo["grupo_id"] = None

    if proceso_reconocimiento is not None:
        if proceso_reconocimiento.poll() is None:
            proceso_reconocimiento.terminate()

        proceso_reconocimiento = None

    return {
        "ok": True,
        "mensaje": "Asistencia finalizada"
    }

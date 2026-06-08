from fastapi import APIRouter

router = APIRouter()

grupo_activo = {
    "grupo_id": None
}

@router.post("/iniciar-asistencia")
def iniciar_asistencia(data: dict):

    grupo_activo["grupo_id"] = data["grupo_id"]

    return {
        "mensaje": "Asistencia iniciada",
        "grupo_id": data["grupo_id"]
    }


@router.get("/grupo-activo")
def obtener_grupo_activo():

    return grupo_activo
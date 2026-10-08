
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import cv2
import numpy as np

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
RUTA_MODELO = BASE_DIR / "ia" / "modelo_lbph.xml"
RUTA_DATASET = BASE_DIR / "ia" / "dataset"

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

modelo = None
personas = []


def cargar_modelo():
    global modelo, personas

    if not RUTA_MODELO.is_file():
        raise HTTPException(
            status_code=503,
            detail="No se encontró el modelo LBPH en el servidor"
        )

    if not RUTA_DATASET.is_dir():
        raise HTTPException(
            status_code=503,
            detail="No se encontró el dataset en el servidor"
        )

    personas = sorted(
        carpeta.name
        for carpeta in RUTA_DATASET.iterdir()
        if carpeta.is_dir()
    )

    if not personas:
        raise HTTPException(
            status_code=503,
            detail="El dataset no contiene alumnos"
        )

    try:
        modelo = cv2.face.LBPHFaceRecognizer_create()
        modelo.read(str(RUTA_MODELO))
    except (AttributeError, cv2.error) as error:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo cargar LBPH: {error}"
        )


@router.post("/reconocer-rostro-web")
async def reconocer_rostro_web(
    imagen: UploadFile = File(...)
):
    global modelo

    if modelo is None:
        cargar_modelo()

    if imagen.content_type not in (
        "image/jpeg",
        "image/png"
    ):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes JPEG o PNG"
        )

    contenido = await imagen.read()

    if len(contenido) > 2_000_000:
        raise HTTPException(
            status_code=413,
            detail="La imagen supera el tamaño permitido"
        )

    datos = np.frombuffer(contenido, np.uint8)
    frame = cv2.imdecode(datos, cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(
            status_code=400,
            detail="No se pudo procesar la imagen"
        )

    gris = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    rostros = detector.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(rostros) == 0:
        return {
            "ok": True,
            "reconocido": False,
            "mensaje": "No se detectó ningún rostro"
        }

    if len(rostros) > 1:
        return {
            "ok": True,
            "reconocido": False,
            "mensaje": "Debe aparecer una sola persona"
        }

    x, y, w, h = rostros[0]

    rostro = gris[y:y+h, x:x+w]
    rostro = cv2.resize(rostro, (150, 150))

    etiqueta, distancia = modelo.predict(rostro)

    if distancia >= 120 or etiqueta >= len(personas):
        return {
            "ok": True,
            "reconocido": False,
            "mensaje": "Rostro desconocido"
        }

    return {
        "ok": True,
        "reconocido": True,
        "alumno": personas[etiqueta],
        "distancia": float(distancia)
    }

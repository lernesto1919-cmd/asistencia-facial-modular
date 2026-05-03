from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de datos
class Asistencia(BaseModel):
    alumno: str


@app.get("/")
def inicio():
    return {
        "mensaje": "Sistema de asistencia facial funcionando"
    }


@app.post("/registrar")
def registrar_asistencia(data: Asistencia):

    print(
        f"Asistencia recibida: {data.alumno}"
    )

    return {
        "status": "ok",
        "alumno": data.alumno
    }
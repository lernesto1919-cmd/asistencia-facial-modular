import requests
import cv2

API_URL = "http://127.0.0.1:8000"

# Cargar detector de rostros
detector_rostro = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Cargar modelo entrenado
modelo = cv2.face.LBPHFaceRecognizer_create()
modelo.read("ia/modelo_lbph.xml")

# Nombres registrados en el modelo
personas = [
    "Luis_Zamora"
]

registrados = set()

# Consultar grupo activo
try:
    respuesta = requests.get(f"{API_URL}/grupo-activo")
    grupo_activo = respuesta.json().get("grupo_id")
except:
    grupo_activo = None

if grupo_activo is None:
    print("No hay grupo activo. Inicia asistencia desde React primero.")
    exit()

print(f"Grupo activo: {grupo_activo}")

# Obtener alumnos del grupo activo
respuesta = requests.get(
    f"{API_URL}/grupos/{grupo_activo}/alumnos"
)

alumnos_grupo = respuesta.json()

nombres_grupo = [
    alumno["nombre"]
    for alumno in alumnos_grupo
]

print("Alumnos del grupo:", nombres_grupo)

# Abrir cámara
camara = cv2.VideoCapture(0)

while True:

    ret, frame = camara.read()

    if not ret:
        print("No se pudo leer la cámara")
        break

    gris = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    rostros = detector_rostro.detectMultiScale(
        gris,
        scaleFactor=1.2,
        minNeighbors=8,
        minSize=(100, 100)
    )

    for (x, y, w, h) in rostros:

        rostro = gris[y:y+h, x:x+w]

        rostro = cv2.resize(
            rostro,
            (150, 150)
        )

        etiqueta, confianza = modelo.predict(rostro)

        if confianza < 120:

            nombre = personas[etiqueta]

            if nombre in nombres_grupo:

                if nombre not in registrados:

                    respuesta = requests.post(
                        f"{API_URL}/registrar",
                        json={
                            "alumno": nombre
                        }
                    )

                    print("Código respuesta:", respuesta.status_code)
                    print("Respuesta texto:", respuesta.text)

                    registrados.add(nombre)

            else:
                print(
                    f"{nombre} no pertenece al grupo activo"
                )

        else:

            nombre = "Desconocido"

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            nombre,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.imshow(
        "Sistema de Asistencia Facial",
        frame
    )

    if cv2.waitKey(1) == 27:
        break

camara.release()
cv2.destroyAllWindows()
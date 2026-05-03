import cv2

# Cargar detector de rostros
detector_rostro = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Cargar modelo entrenado
modelo = cv2.face.LBPHFaceRecognizer_create()
modelo.read("ia/modelo_lbph.xml")

# Nombres registrados
personas = [
    "Luis_Zamora"
]

# Tu cámara (usa el número que te funcionó)
camara = cv2.VideoCapture(0)

while True:

    ret, frame = camara.read()

    if not ret:
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

        rostro = gris[
            y:y+h,
            x:x+w
        ]

        rostro = cv2.resize(
            rostro,
            (150,150)
        )

        etiqueta, confianza = modelo.predict(
            rostro
        )

        if confianza < 80:

            nombre = personas[
                etiqueta
            ]

        else:

            nombre = "Desconocido"

        # Rectángulo
        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0,255,0),
            2
        )

        # Nombre
        cv2.putText(
            frame,
            nombre,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
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
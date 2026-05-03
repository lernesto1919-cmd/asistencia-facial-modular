import cv2

# Detector de rostros incluido en OpenCV
detector_rostro = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Usa el número de cámara que sí te funcionó
camara = cv2.VideoCapture(0)  # cambia si tu cámara era 1, 2, etc.

while True:
    ret, frame = camara.read()

    if not ret:
        print("Error leyendo cámara")
        break

    # Escala de grises
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar rostros
    rostros = detector_rostro.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(50, 50)
    )

    print("Rostros detectados:", len(rostros))

    # Dibujar rectángulo
    for (x, y, w, h) in rostros:
        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

    cv2.imshow("Sistema de Asistencia Facial", frame)

    if cv2.waitKey(1) == 27:
        break

camara.release()
cv2.destroyAllWindows()
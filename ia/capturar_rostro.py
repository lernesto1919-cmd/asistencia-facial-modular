import cv2
import os

nombre = "Luis_Zamora"

ruta = f"ia/dataset/{nombre}"

if not os.path.exists(ruta):
    os.makedirs(ruta)

detector_rostro = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

camara = cv2.VideoCapture(0)  # usa tu número correcto

contador = 0

while contador < 100:

    ret, frame = camara.read()

    if not ret:
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rostros = detector_rostro.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=4
    )

    for (x, y, w, h) in rostros:

        rostro = frame[y:y+h, x:x+w]

        rostro = cv2.resize(rostro, (150, 150))

        archivo = f"{ruta}/{contador}.jpg"

        cv2.imwrite(archivo, rostro)

        contador += 1

        print("Imagen guardada:", contador)

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0,255,0),
            2
        )

    cv2.imshow("Capturando rostros", frame)

    if cv2.waitKey(1) == 27:
        break

camara.release()
cv2.destroyAllWindows()
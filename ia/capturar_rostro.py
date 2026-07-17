import os
import sys
import cv2


def limpiar_nombre(nombre: str) -> str:
    """
    Evita caracteres problemáticos en nombres de carpetas.
    Conserva letras, números, espacios, guiones y guiones bajos.
    """
    caracteres_permitidos = []

    for caracter in nombre.strip():
        if caracter.isalnum() or caracter in (" ", "-", "_"):
            caracteres_permitidos.append(caracter)

    return "".join(caracteres_permitidos).strip()


if len(sys.argv) >= 2:
    nombre = sys.argv[1]
else:
    nombre = input("Nombre exacto del alumno: ")

nombre = limpiar_nombre(nombre)

if not nombre:
    print("El nombre del alumno no es válido")
    sys.exit(1)

ruta = os.path.join("ia", "dataset", nombre)
os.makedirs(ruta, exist_ok=True)

detector_rostro = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("No se pudo abrir la cámara")
    sys.exit(1)

contador = 0
total_imagenes = 100

print(f"Capturando rostro de: {nombre}")
print("Presiona ESC para cancelar")

while contador < total_imagenes:
    ret, frame = camara.read()

    if not ret:
        print("No se pudo leer la cámara")
        break

    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rostros = detector_rostro.detectMultiScale(
        gris,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(100, 100)
    )

    for x, y, w, h in rostros:
        rostro = gris[y:y + h, x:x + w]
        rostro = cv2.resize(rostro, (150, 150))

        archivo = os.path.join(ruta, f"{contador}.jpg")

        if cv2.imwrite(archivo, rostro):
            contador += 1
            print(
                f"Imagen guardada "
                f"{contador}/{total_imagenes}"
            )

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{contador}/{total_imagenes}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # Solo guardar una cara por fotograma.
        break

    cv2.imshow(
        f"Registrar rostro - {nombre}",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        print("Captura cancelada")
        break

camara.release()
cv2.destroyAllWindows()

if contador == total_imagenes:
    print(f"Captura terminada para {nombre}")
else:
    print(f"Se guardaron {contador} imágenes")
import cv2
import os
import numpy as np

ruta_dataset = "ia/dataset"

personas = []
etiquetas = []
caras = []

label_id = 0

for nombre_persona in sorted(os.listdir(ruta_dataset)):

    ruta_persona = os.path.join(
        ruta_dataset,
        nombre_persona
    )

    if os.path.isdir(ruta_persona):

        personas.append(nombre_persona)

        for archivo in os.listdir(ruta_persona):

            ruta_imagen = os.path.join(
                ruta_persona,
                archivo
            )

            imagen = cv2.imread(
                ruta_imagen,
                cv2.IMREAD_GRAYSCALE
            )

            if imagen is not None:

                imagen = cv2.resize(
                    imagen,
                    (150, 150)
                )

                caras.append(imagen)
                etiquetas.append(label_id)

        label_id += 1

if len(caras) == 0:
    print("No hay imágenes para entrenar")
    exit()

modelo = cv2.face.LBPHFaceRecognizer_create()

modelo.train(
    caras,
    np.array(etiquetas)
)

modelo.write("ia/modelo_lbph.xml")

print("Modelo entrenado correctamente")
print("Personas registradas:", personas)
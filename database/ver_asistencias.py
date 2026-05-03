import sqlite3

conexion = sqlite3.connect(
    "database/asistencia.db"
)

cursor = conexion.cursor()

cursor.execute(
    "SELECT * FROM asistencias"
)

registros = cursor.fetchall()

print("\nREGISTROS DE ASISTENCIA:\n")

for registro in registros:
    print(registro)

conexion.close()
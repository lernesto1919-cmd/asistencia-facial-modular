import sqlite3

def conectar():
    conexion = sqlite3.connect("asistencias.db")
    conexion.row_factory = sqlite3.Row
    return conexion
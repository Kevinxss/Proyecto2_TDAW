import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="10.93.44.91",      # 🔹 IP del servidor Ubuntu (donde corre XAMPP)
            user="flaskuser",          # 🔹 Usuario creado para Flask en MySQL
            password="12345",          # 🔹 Contraseña del usuario
            database="pokemon",   # 🔹 Nombre de tu base de datos
            port=3306                  # 🔹 Puerto por defecto de MySQL
        )

        if conexion.is_connected():
            print("conexion exitosa")
            return conexion 

    except Error as e:
        print("❌ Error al conectar con MySQL:", e)
        return None
